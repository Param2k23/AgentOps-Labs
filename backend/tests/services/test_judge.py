import json
import pytest
from unittest.mock import AsyncMock

from services.judge import JudgeService, JudgeParsingException

@pytest.fixture
def mock_llm_service():
    return AsyncMock()

@pytest.fixture
def judge_service(mock_llm_service):
    return JudgeService(llm_service=mock_llm_service)

@pytest.mark.asyncio
async def test_judge_evaluate_success(judge_service, mock_llm_service):
    # Mock LLM returning valid JSON
    valid_json = json.dumps({
        "accuracy": 85.5,
        "groundedness": 90.0,
        "citation_score": 80.0,
        "retrieval_score": 95.0,
        "hallucination_score": 10.0,
        "overall_score": 88.0,
        "feedback": "Good response.",
        "reasoning": "Accurate and well-grounded."
    })
    
    mock_llm_service.generate_raw.return_value = {
        "text": f"```json\n{valid_json}\n```",
        "provider": "gemini",
        "model": "gemini-2.5-flash",
        "latency_ms": 100,
        "prompt_tokens": 50,
        "completion_tokens": 30,
        "total_tokens": 80
    }
    
    result = await judge_service.evaluate(
        task_title="Test Task",
        task_description="Test Desc",
        chunks=["chunk1"],
        ground_truth="truth",
        rubric="rubric",
        generated_response="response"
    )
    
    assert result["accuracy"] == 85.5
    assert result["feedback"] == "Good response."
    assert result["provider"] == "gemini"
    assert mock_llm_service.generate_raw.call_count == 1

@pytest.mark.asyncio
async def test_judge_evaluate_retry_success(judge_service, mock_llm_service):
    # First call returns malformed JSON
    bad_json_result = {
        "text": "This is not json",
        "provider": "gemini",
        "model": "gemini-2.5-flash",
        "latency_ms": 100,
        "prompt_tokens": 50,
        "completion_tokens": 10,
        "total_tokens": 60
    }
    
    # Second call returns valid JSON
    good_json = json.dumps({
        "accuracy": 85.5,
        "groundedness": 90.0,
        "citation_score": 80.0,
        "retrieval_score": 95.0,
        "hallucination_score": 10.0,
        "overall_score": 88.0,
        "feedback": "Fixed JSON.",
        "reasoning": "Reasoning provided."
    })
    good_json_result = {
        "text": good_json,
        "provider": "gemini",
        "model": "gemini-2.5-flash",
        "latency_ms": 150,
        "prompt_tokens": 60,
        "completion_tokens": 30,
        "total_tokens": 90
    }
    
    mock_llm_service.generate_raw.side_effect = [bad_json_result, good_json_result]
    
    result = await judge_service.evaluate(
        task_title="Test Task",
        task_description="Test Desc",
        chunks=["chunk1"],
        ground_truth="truth",
        rubric="rubric",
        generated_response="response"
    )
    
    assert result["feedback"] == "Fixed JSON."
    assert result["total_tokens"] == 150  # 60 + 90
    assert result["latency_ms"] == 250    # 100 + 150
    assert mock_llm_service.generate_raw.call_count == 2

@pytest.mark.asyncio
async def test_judge_evaluate_retry_failure(judge_service, mock_llm_service):
    # Both calls return bad JSON
    bad_json_result = {
        "text": "{ bad json }",
        "provider": "gemini",
        "model": "gemini-2.5-flash"
    }
    
    mock_llm_service.generate_raw.side_effect = [bad_json_result, bad_json_result]
    
    with pytest.raises(JudgeParsingException):
        await judge_service.evaluate(
            task_title="Test Task",
            task_description="Test Desc",
            chunks=["chunk1"],
            ground_truth="truth",
            rubric="rubric",
            generated_response="response"
        )
    
    assert mock_llm_service.generate_raw.call_count == 2
