import json
import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, ValidationError

from services.llm import LLMService

logger = logging.getLogger(__name__)

class JudgeParsingException(Exception):
    """Exception raised when the Judge output cannot be parsed into the expected JSON schema."""
    pass

class JudgeResult(BaseModel):
    accuracy: float = Field(..., ge=0, le=100, description="Score between 0 and 100 representing correctness.")
    groundedness: float = Field(..., ge=0, le=100, description="Score between 0 and 100 for how well response is supported by context.")
    citation_score: float = Field(..., ge=0, le=100, description="Score between 0 and 100 for correct citation usage.")
    retrieval_score: float = Field(..., ge=0, le=100, description="Score between 0 and 100 for quality of retrieved context.")
    hallucination_score: float = Field(..., ge=0, le=100, description="Score between 0 and 100 for presence of hallucinations (lower is better, or higher means less hallucination depending on metric - assume standard score where 0 means no hallucination and 100 means full hallucination, actually let's stick to 0-100 where 100 is best, wait, original mock is 0.0 to 15.0 for hallucination. We will just use 0-100 scale).")
    overall_score: float = Field(..., ge=0, le=100, description="Aggregate overall score between 0 and 100.")
    feedback: str = Field(..., description="Detailed textual feedback explaining the scores.")
    reasoning: Optional[str] = Field(default=None, description="Step-by-step reasoning for the assigned scores.")

class JudgeService:
    """Service to evaluate generated responses using an LLM-as-a-judge."""

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def _build_evaluation_prompt(
        self,
        task_title: str,
        task_description: str,
        chunks: List[str],
        ground_truth: str | None,
        rubric: str | None,
        generated_response: str
    ) -> str:
        context_str = "\n\n".join(chunks) if chunks else "No relevant context provided."
        
        prompt = (
            "You are an expert AI judge evaluating a generated response against a specific task.\n\n"
            f"### Task Title:\n{task_title}\n\n"
            f"### Task Description:\n{task_description}\n\n"
            f"### Retrieved Context:\n{context_str}\n\n"
            f"### Ground Truth (if any):\n{ground_truth or 'N/A'}\n\n"
            f"### Grading Rubric (if any):\n{rubric or 'N/A'}\n\n"
            f"### Generated Response to Evaluate:\n{generated_response}\n\n"
            "### Instructions:\n"
            "Evaluate the Generated Response based on the Task Description, Retrieved Context, and Rubric.\n"
            "You MUST output STRICT VALID JSON only. Do not wrap it in markdown block quotes (```json...```). "
            "Do not include any other text before or after the JSON.\n\n"
            "The JSON must have exactly the following keys, with numeric scores strictly between 0 and 100:\n"
            "- accuracy (number)\n"
            "- groundedness (number)\n"
            "- citation_score (number)\n"
            "- retrieval_score (number)\n"
            "- hallucination_score (number, where 0 is perfect/no hallucination, or use the required scale)\n"
            "- overall_score (number)\n"
            "- feedback (string)\n"
            "- reasoning (string)\n"
        )
        return prompt

    def _build_retry_prompt(self, bad_json: str, error_msg: str) -> str:
        return (
            "You are an expert AI data formatter. "
            "The following JSON is malformed or missing fields. "
            "Please fix it and return ONLY valid JSON matching the schema.\n\n"
            f"Error encountered: {error_msg}\n\n"
            f"Bad JSON:\n{bad_json}\n\n"
            "Remember: Output STRICT VALID JSON only. No markdown formatting, no other text."
        )

    def _parse_json_result(self, text: str) -> JudgeResult:
        # Try to clean markdown formatting if the model still outputs it
        text = text.strip()
        if text.startswith("```json"):
            text = text[len("```json"):]
        if text.startswith("```"):
            text = text[len("```"):]
        if text.endswith("```"):
            text = text[:-len("```")]
        text = text.strip()

        try:
            return JudgeResult.model_validate_json(text)
        except ValidationError as e:
            raise JudgeParsingException(f"Schema validation failed: {str(e)}")
        except json.JSONDecodeError as e:
            raise JudgeParsingException(f"Invalid JSON format: {str(e)}")

    async def evaluate(
        self,
        task_title: str,
        task_description: str,
        chunks: List[str],
        ground_truth: str | None,
        rubric: str | None,
        generated_response: str
    ) -> Dict[str, Any]:
        """
        Evaluates the generated response and returns a dictionary with scores and metadata.
        Retries once if parsing fails.
        """
        prompt = self._build_evaluation_prompt(
            task_title, task_description, chunks, ground_truth, rubric, generated_response
        )

        try:
            result = await self.llm_service.generate_raw(prompt)
            raw_text = result.get("text", "")
            judge_result = self._parse_json_result(raw_text)
        except JudgeParsingException as e:
            logger.warning(f"Judge output parsing failed. Retrying... Error: {str(e)}")
            # Retry logic
            retry_prompt = self._build_retry_prompt(result.get("text", ""), str(e))
            try:
                retry_result = await self.llm_service.generate_raw(retry_prompt)
                raw_text = retry_result.get("text", "")
                judge_result = self._parse_json_result(raw_text)
                # Combine token usage from both calls if needed, but we can just use the retry's metadata for simplicity,
                # or manually add them up. We will just append the total tokens.
                result["total_tokens"] = result.get("total_tokens", 0) + retry_result.get("total_tokens", 0)
                result["latency_ms"] = result.get("latency_ms", 0) + retry_result.get("latency_ms", 0)
            except JudgeParsingException as e2:
                raise JudgeParsingException(f"Failed to parse Judge output after retry. Original Error: {str(e)}. Retry Error: {str(e2)}")
        except Exception as ex:
            raise Exception(f"Unexpected error during judge evaluation: {str(ex)}")

        # Convert JudgeResult to dictionary and merge with LLM metadata
        scores = judge_result.model_dump()
        
        # Include the provider metadata
        return {
            **scores,
            "provider": result.get("provider"),
            "model": result.get("model"),
            "latency_ms": result.get("latency_ms"),
            "prompt_tokens": result.get("prompt_tokens"),
            "completion_tokens": result.get("completion_tokens"),
            "total_tokens": result.get("total_tokens")
        }
