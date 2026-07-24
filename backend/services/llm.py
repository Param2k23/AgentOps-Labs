import logging
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, List

from google import genai
from google.genai import types
from google.genai.errors import APIError

from core.exceptions import BadRequestException
from config.settings import get_settings

logger = logging.getLogger(__name__)

class LLMException(Exception):
    """Base exception for LLM-related errors."""
    pass

class ProviderInterface(ABC):
    """Interface for all LLM providers."""
    
    @abstractmethod
    async def generate(self, prompt: str, model: str, timeout: int, temperature: float) -> Dict[str, Any]:
        """Generate a response from the LLM provider.
        
        Args:
            prompt: The full prompt string.
            model: The specific model to use (e.g. gemini-2.5-flash).
            timeout: Timeout in seconds.
            temperature: Sampling temperature.
            
        Returns:
            Dict containing:
                - text: The generated response string.
                - provider: The name of the provider.
                - model: The actual model used.
                - prompt_tokens: Number of tokens in prompt (if available).
                - completion_tokens: Number of tokens in response (if available).
                - total_tokens: Total tokens used (if available).
        """
        pass

class GeminiProvider(ProviderInterface):
    """Gemini implementation of the ProviderInterface."""
    
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or get_settings().gemini_api_key
        if not self.api_key:
            # We don't raise immediately to allow graceful failure during generation
            logger.warning("Gemini API key is missing.")
        
        # In actual execution, genai.Client uses GEMINI_API_KEY env if not passed explicitly,
        # but we pass it if we have it to support multiple keys or explicit settings.
        self.client = genai.Client(api_key=self.api_key or "dummy-key-to-prevent-init-error")

    async def generate(self, prompt: str, model: str, timeout: int, temperature: float) -> Dict[str, Any]:
        if not self.api_key:
            raise LLMException("Gemini API key is missing. Please configure GEMINI_API_KEY.")
            
        try:
            # Using synchronous call in a thread or asyncio equivalent.
            # google-genai supports async via client.aio.models.generate_content
            response = await self.client.aio.models.generate_content(
                model=model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=temperature,
                )
            )
            
            content = response.text or ""
            
            usage = response.usage_metadata
            prompt_tokens = usage.prompt_token_count if usage else 0
            completion_tokens = usage.candidates_token_count if usage else 0
            total_tokens = usage.total_token_count if usage else 0
            
            return {
                "text": content,
                "provider": "gemini",
                "model": model,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens,
            }
            
        except APIError as e:
            logger.error(f"Gemini API error: {e}")
            raise LLMException(f"Gemini API error: {e.message}")
        except Exception as e:
            logger.error(f"Unexpected Gemini provider error: {e}")
            raise LLMException(f"Unexpected LLM error: {str(e)}")

class LLMService:
    """Service orchestrating prompt construction and provider invocation."""
    
    def __init__(self, provider: ProviderInterface, model: str, timeout: int, temperature: float):
        self.provider = provider
        self.model = model
        self.timeout = timeout
        self.temperature = temperature
        
    def _build_prompt(self, task_title: str, task_description: str, chunks: List[str]) -> str:
        """Constructs the structured prompt."""
        context_str = "\n\n".join(chunks) if chunks else "No relevant context found."
        
        prompt = (
            "You are an enterprise AI assistant.\n\n"
            f"Task:\nTitle: {task_title}\n"
            f"Description: {task_description}\n\n"
            f"Relevant Context:\n{context_str}\n\n"
            "Instructions:\n"
            "Only answer using the provided context whenever possible. Do not invent information.\n\n"
            "Answer:\n"
        )
        return prompt

    async def generate_response(
        self, 
        task_title: str, 
        task_description: str, 
        chunks: List[str]
    ) -> Dict[str, Any]:
        """Generates a response using the injected provider.
        
        Args:
            task_title: The title of the task.
            task_description: The description of the task.
            chunks: List of relevant context chunks.
            
        Returns:
            Dict containing the generated text, metadata, and latency.
        """
        prompt = self._build_prompt(task_title, task_description, chunks)
        
        logger.info(f"Invoking LLM provider using model {self.model}")
        
        start_time = time.perf_counter()
        
        try:
            result = await self.provider.generate(
                prompt=prompt,
                model=self.model,
                timeout=self.timeout,
                temperature=self.temperature
            )
            
            end_time = time.perf_counter()
            latency_ms = int((end_time - start_time) * 1000)
            
            result["latency_ms"] = latency_ms
            
            logger.info(f"LLM request successful. Latency: {latency_ms}ms. Tokens: {result.get('total_tokens', 0)}")
            
            return result
            
        except Exception as e:
            end_time = time.perf_counter()
            latency_ms = int((end_time - start_time) * 1000)
            logger.error(f"LLM request failed after {latency_ms}ms. Error: {str(e)}")
            raise e

    async def generate_raw(self, prompt: str) -> Dict[str, Any]:
        """Generates a response using a raw provided prompt (bypassing default formatting).
        Useful for custom instructions, like LLM-as-a-judge logic.
        """
        logger.info(f"Invoking LLM provider using model {self.model} with raw prompt")
        
        start_time = time.perf_counter()
        
        try:
            result = await self.provider.generate(
                prompt=prompt,
                model=self.model,
                timeout=self.timeout,
                temperature=self.temperature
            )
            
            end_time = time.perf_counter()
            latency_ms = int((end_time - start_time) * 1000)
            
            result["latency_ms"] = latency_ms
            
            logger.info(f"Raw LLM request successful. Latency: {latency_ms}ms. Tokens: {result.get('total_tokens', 0)}")
            
            return result
            
        except Exception as e:
            end_time = time.perf_counter()
            latency_ms = int((end_time - start_time) * 1000)
            logger.error(f"Raw LLM request failed after {latency_ms}ms. Error: {str(e)}")
            raise e
