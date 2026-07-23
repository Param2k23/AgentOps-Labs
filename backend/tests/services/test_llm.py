import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from services.llm import LLMService, GeminiProvider, LLMException
from core.exceptions import BadRequestException

@pytest.fixture
def mock_provider():
    provider = AsyncMock()
    provider.generate.return_value = {
        "text": "Mock LLM Response",
        "provider": "gemini",
        "model": "mock-model",
        "prompt_tokens": 10,
        "completion_tokens": 20,
        "total_tokens": 30,
    }
    return provider

@pytest.fixture
def llm_service(mock_provider):
    return LLMService(
        provider=mock_provider,
        model="test-model",
        timeout=30,
        temperature=0.0
    )

@pytest.mark.asyncio
async def test_llm_service_generate_success(llm_service, mock_provider):
    result = await llm_service.generate_response(
        task_title="Test Task",
        task_description="Test Description",
        chunks=["Context 1", "Context 2"]
    )
    
    assert result["text"] == "Mock LLM Response"
    assert "latency_ms" in result
    
    mock_provider.generate.assert_called_once()
    kwargs = mock_provider.generate.call_args.kwargs
    assert kwargs["model"] == "test-model"
    assert "Context 1" in kwargs["prompt"]
    assert "Context 2" in kwargs["prompt"]

@pytest.mark.asyncio
async def test_llm_service_generate_failure(llm_service, mock_provider):
    mock_provider.generate.side_effect = LLMException("API Error")
    
    with pytest.raises(LLMException) as excinfo:
        await llm_service.generate_response(
            task_title="Test Task",
            task_description="Test Description",
            chunks=[]
        )
    assert "API Error" in str(excinfo.value)

@pytest.mark.asyncio
async def test_gemini_provider_missing_key():
    with patch("services.llm.get_settings") as mock_settings:
        mock_settings.return_value.gemini_api_key = None
        provider = GeminiProvider()
        
        with pytest.raises(LLMException) as excinfo:
            await provider.generate("prompt", "model", 30, 0.0)
        assert "API key is missing" in str(excinfo.value)
