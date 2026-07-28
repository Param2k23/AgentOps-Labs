import logging
import time
import asyncio
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from google import genai
from google.genai import types
from google.genai.errors import APIError
import openai

from core.exceptions import BadRequestException
from config.settings import get_settings
from config.models import MODEL_REGISTRY

logger = logging.getLogger(__name__)

class LLMException(Exception):
    """Base exception for LLM-related errors."""
    pass

class LLMRateLimitException(LLMException):
    pass

class LLMTimeoutException(LLMException):
    pass

class LLMProviderException(LLMException):
    pass

class LLMAuthException(LLMException):
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
            
        max_retries = 3
        base_delay = 1
        
        for attempt in range(max_retries + 1):
            try:
                response = await self.client.aio.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=temperature,
                    )
                )
                
                content = response.text or ""
                # Gemini SDK doesn't expose usage tokens as easily in the same structure,
                # we'd need to count them or extract from response metadata if available.
                # For now, we mock token counts for Gemini if unavailable.
                token_count = len(content.split()) * 1.3
                
                return {
                    "text": content,
                    "provider": "gemini",
                    "model": model,
                    "prompt_tokens": int(len(prompt.split()) * 1.3),
                    "completion_tokens": int(token_count),
                    "total_tokens": int(len(prompt.split()) * 1.3 + token_count),
                }
            except Exception as e:
                import google.genai.errors
                if isinstance(e, google.genai.errors.APIError) and e.code == 429:
                    if attempt < max_retries:
                        delay = base_delay * (2 ** attempt)
                        logger.warning(f"Provider: Gemini, Model: {model}, Attempt: {attempt + 1}, Status: Rate Limited. Retrying in {delay} seconds...")
                        await asyncio.sleep(delay)
                        continue
                logger.error(f"Gemini API error: {e}")
                raise LLMException(f"Gemini API error: {e.message}")
            except Exception as e:
                if "429" in str(e) and attempt < max_retries:
                    delay = base_delay * (2 ** attempt)
                    logger.warning(f"Provider: Gemini, Model: {model}, Attempt: {attempt + 1}, Status: Rate Limited. Retrying in {delay} seconds...")
                    await asyncio.sleep(delay)
                    continue
                logger.error(f"Unexpected Gemini provider error: {e}")
                raise LLMException(f"Unexpected LLM error: {str(e)}")

class OpenRouterProvider(ProviderInterface):
    """OpenRouter implementation of the ProviderInterface using the OpenAI client."""
    
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or get_settings().openrouter_api_key
        if not self.api_key:
            logger.warning("OpenRouter API key is missing. Ensure OPENROUTER_API_KEY is set.")
            
        self.client = openai.AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key or "dummy-key-to-prevent-init-error"
        )

    async def generate(self, prompt: str, model: str, timeout: int, temperature: float) -> Dict[str, Any]:
        if not self.api_key:
            raise LLMException("OpenRouter API key is missing.")
            
        max_retries = 3
        base_delay = 1
        
        for attempt in range(max_retries + 1):
            try:
                response = await self.client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                    timeout=timeout
                )
                
                if not response.choices:
                    raise openai.InternalServerError(f"No choices returned. Response: {response}", response=None, body=None)

                content = response.choices[0].message.content or ""
                usage = response.usage
                
                prompt_tokens = usage.prompt_tokens if usage else 0
                completion_tokens = usage.completion_tokens if usage else 0
                total_tokens = usage.total_tokens if usage else 0
                
                return {
                    "text": content,
                    "provider": "openrouter",
                    "model": model,
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": total_tokens,
                }
                
            except openai.RateLimitError as e:
                if attempt < max_retries:
                    delay = base_delay * (2 ** attempt)
                    logger.warning(f"Provider: OpenRouter, Model: {model}, Attempt: {attempt + 1}, Status: Rate Limited. Retrying in {delay} seconds...")
                    await asyncio.sleep(delay)
                    continue
                logger.error(f"OpenRouter Rate Limited after {max_retries} retries: {e}")
                raise LLMRateLimitException(f"Rate limited by OpenRouter. Model {model} is temporarily rate limited.")
            except openai.APITimeoutError as e:
                if attempt < max_retries:
                    delay = base_delay * (2 ** attempt)
                    logger.warning(f"Provider: OpenRouter, Model: {model}, Attempt: {attempt + 1}, Status: Timeout. Retrying in {delay} seconds...")
                    await asyncio.sleep(delay)
                    continue
                logger.error(f"OpenRouter timeout after {max_retries} retries: {e}")
                raise LLMTimeoutException(f"Timeout while communicating with OpenRouter.")
            except openai.AuthenticationError as e:
                logger.error(f"OpenRouter Authentication Error: {e}")
                raise LLMAuthException(f"Invalid API key for OpenRouter.")
            except openai.InternalServerError as e:
                if attempt < max_retries:
                    delay = base_delay * (2 ** attempt)
                    logger.warning(f"Provider: OpenRouter, Model: {model}, Attempt: {attempt + 1}, Status: Internal Server Error. Retrying in {delay} seconds...")
                    await asyncio.sleep(delay)
                    continue
                logger.error(f"OpenRouter provider error: {e}")
                raise LLMProviderException(f"OpenRouter provider error: {e}")
            except openai.OpenAIError as e:
                logger.error(f"OpenRouter API error: {e}")
                raise LLMException(f"OpenRouter API error: {str(e)}")
            except Exception as e:
                logger.error(f"Unexpected OpenRouter provider error: {e}")
                raise LLMException(f"Unexpected LLM error: {str(e)}")

class LLMService:
    """Service orchestrating prompt construction and provider invocation."""
    
    def __init__(self, default_provider: ProviderInterface, default_model: str, timeout: int, temperature: float):
        self.default_provider = default_provider
        self.default_model = default_model
        self.timeout = timeout
        self.temperature = temperature
        
        # Initialize providers lazily or upfront
        self._providers = {
            "gemini": GeminiProvider(),
            "openrouter": OpenRouterProvider()
        }
        
    def _get_provider_for_model(self, model: str) -> ProviderInterface:
        model_info = MODEL_REGISTRY.get(model)
        if model_info:
            provider_type = model_info["provider"]
            return self._providers.get(provider_type, self.default_provider)
        return self.default_provider
        
    async def generate_response(
        self, 
        prompt: str, 
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generates a response using the injected provider.
        
        Args:
            prompt: The full prompt string to send to the model.
            model: Optional model to override the default.
            
        Returns:
            Dict containing the generated text, metadata, and latency.
        """
        target_model = model or self.default_model
        
        logger.info(f"Invoking LLM provider using model {target_model}")
        
        start_time = time.perf_counter()
        
        fallback_models = []
        if getattr(get_settings(), "enable_fallback", True) and "free" in target_model.lower():
            fallback_models = [
                "meta-llama/llama-3.1-8b-instruct:free",
                "nvidia/nemotron-3-super-120b-a12b:free",
                "nvidia/nemotron-3-ultra-550b-a55b:free"
            ]
            if target_model in fallback_models:
                fallback_models.remove(target_model)
                
        models_to_try = [target_model] + fallback_models
        
        for idx, current_model in enumerate(models_to_try):
            provider = self._get_provider_for_model(current_model)
            try:
                result = await provider.generate(
                    prompt=prompt,
                    model=current_model,
                    timeout=self.timeout,
                    temperature=self.temperature
                )
                
                end_time = time.perf_counter()
                latency_ms = int((end_time - start_time) * 1000)
                
                result["latency_ms"] = latency_ms
                
                if current_model != target_model:
                    logger.info(f"Fallback successful. Ultimately used model: {current_model}")
                
                logger.info(f"LLM request successful. Latency: {latency_ms}ms. Tokens: {result.get('total_tokens', 0)}")
                return result
                
            except Exception as e:
                if idx < len(models_to_try) - 1:
                    logger.warning(f"Model {current_model} failed with {type(e).__name__}. Falling back to {models_to_try[idx+1]}")
                    continue
                else:
                    end_time = time.perf_counter()
                    latency_ms = int((end_time - start_time) * 1000)
                    logger.error(f"LLM request failed after {latency_ms}ms. Error: {str(e)}")
                    raise e

    async def generate_raw(self, prompt: str, model: Optional[str] = None) -> Dict[str, Any]:
        """Generates a response using a raw provided prompt (bypassing default formatting).
        Useful for custom instructions, like LLM-as-a-judge logic.
        """
        target_model = model or self.default_model
        
        logger.info(f"Invoking LLM provider using model {target_model} with raw prompt")
        
        start_time = time.perf_counter()
        
        fallback_models = []
        if getattr(get_settings(), "enable_fallback", True) and "free" in target_model.lower():
            fallback_models = [
                "meta-llama/llama-3.1-8b-instruct:free",
                "nvidia/nemotron-3-super-120b-a12b:free",
                "nvidia/nemotron-3-ultra-550b-a55b:free"
            ]
            if target_model in fallback_models:
                fallback_models.remove(target_model)
                
        models_to_try = [target_model] + fallback_models
        
        for idx, current_model in enumerate(models_to_try):
            provider = self._get_provider_for_model(current_model)
            try:
                result = await provider.generate(
                    prompt=prompt,
                    model=current_model,
                    timeout=self.timeout,
                    temperature=self.temperature
                )
                
                end_time = time.perf_counter()
                latency_ms = int((end_time - start_time) * 1000)
                
                result["latency_ms"] = latency_ms
                
                if current_model != target_model:
                    logger.info(f"Fallback successful in raw mode. Ultimately used model: {current_model}")
                
                logger.info(f"Raw LLM request successful. Latency: {latency_ms}ms. Tokens: {result.get('total_tokens', 0)}")
                return result
                
            except Exception as e:
                if idx < len(models_to_try) - 1:
                    logger.warning(f"Model {current_model} failed with {type(e).__name__}. Falling back to {models_to_try[idx+1]}")
                    continue
                else:
                    end_time = time.perf_counter()
                    latency_ms = int((end_time - start_time) * 1000)
                    logger.error(f"Raw LLM request failed after {latency_ms}ms. Error: {str(e)}")
                    raise e
