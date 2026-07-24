import pytest
import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

from services.evaluation_engine import EvaluationEngineService
from models.evaluation_run import EvaluationRun
from models.task import Task
from core.exceptions import NotFoundException

@pytest.fixture
def mock_eval_run_repo():
    return AsyncMock()

@pytest.fixture
def mock_task_repo():
    return AsyncMock()

@pytest.fixture
def mock_retrieval_service():
    service = AsyncMock()
    service.retrieve_chunks.return_value = [
        {"chunk": MagicMock(text="Chunk 1 content")}
    ]
    return service

@pytest.fixture
def mock_llm_service():
    service = AsyncMock()
    service.generate_response.return_value = {
        "text": "Real generated response",
        "provider": "gemini",
        "model": "gemini-2.5-flash",
        "latency_ms": 500,
        "prompt_tokens": 50,
        "completion_tokens": 20,
        "total_tokens": 70,
    }
    return service

@pytest.fixture
def mock_judge_service():
    service = AsyncMock()
    service.evaluate.return_value = {
        "accuracy": 85.0,
        "groundedness": 90.0,
        "citation_score": 80.0,
        "retrieval_score": 95.0,
        "hallucination_score": 10.0,
        "overall_score": 88.0,
        "feedback": "Test feedback",
        "prompt_tokens": 100,
        "completion_tokens": 50,
        "total_tokens": 150,
        "latency_ms": 1000
    }
    return service

@pytest.fixture
def engine_service(mock_eval_run_repo, mock_task_repo, mock_retrieval_service, mock_llm_service, mock_judge_service):
    return EvaluationEngineService(
        evaluation_run_repository=mock_eval_run_repo,
        task_repository=mock_task_repo,
        retrieval_service=mock_retrieval_service,
        llm_service=mock_llm_service,
        judge_service=mock_judge_service
    )

@pytest.mark.asyncio
async def test_execute_run_success(engine_service, mock_eval_run_repo, mock_task_repo, mock_llm_service, mock_judge_service):
    run_id = uuid.uuid4()
    now = datetime.now(timezone.utc)
    mock_run = EvaluationRun(
        id=run_id, 
        task_id=uuid.uuid4(), 
        world_id=uuid.uuid4(),
        status="pending",
        created_at=now,
        updated_at=now
    )
    mock_eval_run_repo.get.return_value = mock_run
    mock_eval_run_repo.update.return_value = mock_run
    
    mock_task = Task(id=mock_run.task_id, title="Task Title", description="Task Desc")
    mock_task_repo.get.return_value = mock_task
    
    result = await engine_service.execute_run(run_id)
    
    assert mock_llm_service.generate_response.called
    kwargs = mock_llm_service.generate_response.call_args.kwargs
    assert kwargs["task_title"] == "Task Title"
    
    assert mock_judge_service.evaluate.called
    judge_kwargs = mock_judge_service.evaluate.call_args.kwargs
    assert judge_kwargs["generated_response"] == "Real generated response"
    
    update_calls = mock_eval_run_repo.update.call_args_list
    assert len(update_calls) == 2
    final_call_kwargs = update_calls[-1].kwargs
    assert final_call_kwargs["status"] == "completed"
    assert final_call_kwargs["response"] == "Real generated response"
    assert final_call_kwargs["provider"] == "gemini"
    assert final_call_kwargs["latency_ms"] == 1500  # 500 from llm + 1000 from judge
    assert final_call_kwargs["total_tokens"] == 220 # 70 from llm + 150 from judge
    assert final_call_kwargs["accuracy"] == 85.0
    assert final_call_kwargs["feedback"] == "Test feedback"

@pytest.mark.asyncio
async def test_execute_run_llm_failure(engine_service, mock_eval_run_repo, mock_task_repo, mock_llm_service):
    run_id = uuid.uuid4()
    now = datetime.now(timezone.utc)
    mock_run = EvaluationRun(
        id=run_id, 
        task_id=uuid.uuid4(), 
        world_id=uuid.uuid4(),
        status="pending",
        created_at=now,
        updated_at=now
    )
    mock_eval_run_repo.get.return_value = mock_run
    mock_eval_run_repo.update.return_value = mock_run
    
    mock_task = Task(id=mock_run.task_id, title="Task Title", description="Task Desc")
    mock_task_repo.get.return_value = mock_task
    
    mock_llm_service.generate_response.side_effect = Exception("Gemini API Down")
    
    result = await engine_service.execute_run(run_id)
    
    update_calls = mock_eval_run_repo.update.call_args_list
    assert len(update_calls) == 2
    final_call_kwargs = update_calls[-1].kwargs
    assert final_call_kwargs["status"] == "failed"
    assert "LLM Generation Failed" in final_call_kwargs["feedback"]

@pytest.mark.asyncio
async def test_execute_run_judge_failure(engine_service, mock_eval_run_repo, mock_task_repo, mock_llm_service, mock_judge_service):
    run_id = uuid.uuid4()
    now = datetime.now(timezone.utc)
    mock_run = EvaluationRun(
        id=run_id, 
        task_id=uuid.uuid4(), 
        world_id=uuid.uuid4(),
        status="pending",
        created_at=now,
        updated_at=now
    )
    mock_eval_run_repo.get.return_value = mock_run
    mock_eval_run_repo.update.return_value = mock_run
    
    mock_task = Task(id=mock_run.task_id, title="Task Title", description="Task Desc")
    mock_task_repo.get.return_value = mock_task
    
    from services.judge import JudgeParsingException
    mock_judge_service.evaluate.side_effect = JudgeParsingException("Judge failed")
    
    result = await engine_service.execute_run(run_id)
    
    update_calls = mock_eval_run_repo.update.call_args_list
    assert len(update_calls) == 2
    final_call_kwargs = update_calls[-1].kwargs
    assert final_call_kwargs["status"] == "failed"
    assert "Judge Evaluation Failed" in final_call_kwargs["feedback"]
