import random
from datetime import datetime, timezone
from uuid import UUID

from core.exceptions import NotFoundException, BadRequestException
from models.evaluation_run import EvaluationRun
from repositories.evaluation_run import EvaluationRunRepository
from repositories.task import TaskRepository
from schemas.evaluation_run import EvaluationRunResponse

from services.retrieval import RetrievalService
from services.llm import LLMService
from services.judge import JudgeService, JudgeParsingException

class EvaluationEngineService:
    """Service responsible for executing EvaluationRuns."""

    def __init__(
        self,
        evaluation_run_repository: EvaluationRunRepository,
        task_repository: TaskRepository,
        retrieval_service: RetrievalService,
        llm_service: LLMService,
        judge_service: JudgeService,
    ):
        self.evaluation_run_repository = evaluation_run_repository
        self.task_repository = task_repository
        self.retrieval_service = retrieval_service
        self.llm_service = llm_service
        self.judge_service = judge_service

    async def execute_run(self, eval_run_id: UUID) -> EvaluationRunResponse:
        """Executes the evaluation run and returns the updated run."""
        
        # 1. Load EvaluationRun
        eval_run_model = await self.evaluation_run_repository.get(eval_run_id)
        if not eval_run_model:
            raise NotFoundException(detail="Evaluation run not found.")
            
        if eval_run_model.status != "pending":
            raise BadRequestException(detail=f"Evaluation run is already in status: {eval_run_model.status}")

        # Update status to running
        eval_run_model = await self.evaluation_run_repository.update(
            eval_run_model,
            status="running",
            started_at=datetime.now(timezone.utc)
        )

        # 2. Load Task and Document
        task = await self.task_repository.get(eval_run_model.task_id)
        if not task:
            await self.evaluation_run_repository.update(eval_run_model, status="failed", feedback="Task not found")
            raise NotFoundException(detail="Task not found.")
            
        # Retrieve chunks for context
        try:
            top_chunks = await self.retrieval_service.retrieve_chunks(task.id, top_k=3)
            chunk_texts = [item["chunk"].text for item in top_chunks]
        except Exception:
            chunk_texts = []

        # 3. Generate Model Response using real LLM
        try:
            llm_result = await self.llm_service.generate_response(
                task_title=task.title or "Untitled Task",
                task_description=task.description or "",
                chunks=chunk_texts
            )
            generated_response = llm_result.get("text", "")
            provider = llm_result.get("provider")
            model = llm_result.get("model")
            latency_ms = llm_result.get("latency_ms")
            prompt_tokens = llm_result.get("prompt_tokens", 0)
            completion_tokens = llm_result.get("completion_tokens", 0)
            total_tokens = llm_result.get("total_tokens", 0)
        except Exception as e:
            # Handle LLM failure gracefully
            await self.evaluation_run_repository.update(
                eval_run_model,
                status="failed",
                feedback=f"LLM Generation Failed: {str(e)}",
                completed_at=datetime.now(timezone.utc)
            )
            return EvaluationRunResponse.model_validate(eval_run_model)

        # 4. Evaluate the response against task's expected_output/rubric (LLM-as-a-judge)
        try:
            judge_result = await self.judge_service.evaluate(
                task_title=task.title or "Untitled Task",
                task_description=task.description or "",
                chunks=chunk_texts,
                ground_truth=task.ground_truth,
                rubric=task.rubric,
                generated_response=generated_response
            )
            accuracy = judge_result.get("accuracy", 0.0)
            groundedness = judge_result.get("groundedness", 0.0)
            citation_score = judge_result.get("citation_score", 0.0)
            retrieval_score = judge_result.get("retrieval_score", 0.0)
            hallucination_score = judge_result.get("hallucination_score", 0.0)
            overall_score = judge_result.get("overall_score", 0.0)
            feedback = judge_result.get("feedback", "No feedback provided.")
            
            # Combine token usage from both generator and judge
            prompt_tokens += judge_result.get("prompt_tokens", 0)
            completion_tokens += judge_result.get("completion_tokens", 0)
            total_tokens += judge_result.get("total_tokens", 0)
            
            # Use judge's model for final attribution if desired, or keep generator's model.
            # We'll stick to generator's model, but update the total tokens.
            latency_ms += judge_result.get("latency_ms", 0)
            
        except JudgeParsingException as e:
            await self.evaluation_run_repository.update(
                eval_run_model,
                status="failed",
                feedback=f"Judge Evaluation Failed: {str(e)}",
                completed_at=datetime.now(timezone.utc)
            )
            return EvaluationRunResponse.model_validate(eval_run_model)
        except Exception as e:
            await self.evaluation_run_repository.update(
                eval_run_model,
                status="failed",
                feedback=f"Judge Unexpected Error: {str(e)}",
                completed_at=datetime.now(timezone.utc)
            )
            return EvaluationRunResponse.model_validate(eval_run_model)

        # Tool success is not part of the standard metrics schema for now, keep default or 100
        tool_success = 100.0

        # 5. Update EvaluationRun
        eval_run_model = await self.evaluation_run_repository.update(
            eval_run_model,
            status="completed",
            completed_at=datetime.now(timezone.utc),
            response=generated_response,
            accuracy=accuracy,
            groundedness=groundedness,
            citation_score=citation_score,
            retrieval_score=retrieval_score,
            hallucination_score=hallucination_score,
            tool_success=tool_success,
            overall_score=overall_score,
            feedback=feedback,
            provider=provider,
            model_name=model,
            latency_ms=latency_ms,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens
        )

        return EvaluationRunResponse.model_validate(eval_run_model)
