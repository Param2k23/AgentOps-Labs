import uuid
import asyncio
from typing import List

from fastapi import BackgroundTasks

from core.database import AsyncSessionFactory
from models.experiment import Experiment
from models.evaluation_run import EvaluationRun
from repositories.experiment import ExperimentRepository
from repositories.evaluation_run import EvaluationRunRepository
from repositories.task import TaskRepository
from repositories.document import DocumentRepository
from repositories.document_chunk import DocumentChunkRepository
from services.evaluation_engine import EvaluationEngineService
from services.retrieval import RetrievalService
from services.embedding import EmbeddingService
from services.llm import LLMService, GeminiProvider
from services.judge import JudgeService
from config.settings import get_settings


async def execute_run_in_background(run_id: uuid.UUID):
    """Creates a new DB session and executes the run."""
    async with AsyncSessionFactory() as session:
        # We must re-instantiate the engine service with the new session
        eval_run_repo = EvaluationRunRepository(session=session)
        task_repo = TaskRepository(session=session)
        
        doc_repo = DocumentRepository(session=session)
        chunk_repo = DocumentChunkRepository(session=session)
        embedding_svc = EmbeddingService()
        retrieval_svc = RetrievalService(doc_repo, chunk_repo, task_repo, embedding_svc)
        
        settings = get_settings()
        provider = GeminiProvider(api_key=settings.gemini_api_key)
        llm_svc = LLMService(
            default_provider=provider,
            default_model=settings.gemini_model,
            timeout=settings.llm_timeout,
            temperature=settings.llm_temperature
        )
        judge_svc = JudgeService(llm_service=llm_svc)
        
        engine = EvaluationEngineService(
            evaluation_run_repository=eval_run_repo,
            task_repository=task_repo,
            retrieval_service=retrieval_svc,
            llm_service=llm_svc,
            judge_service=judge_svc,
        )
        
        try:
            await engine.execute_run(run_id)
        except Exception as e:
            # Let it fail gracefully
            pass

class ExperimentService:
    def __init__(
        self,
        experiment_repository: ExperimentRepository,
        evaluation_run_repository: EvaluationRunRepository,
        task_repository: TaskRepository,
    ):
        self.experiment_repository = experiment_repository
        self.evaluation_run_repository = evaluation_run_repository
        self.task_repository = task_repository

    async def create_experiment_and_run(
        self, 
        name: str, 
        description: str | None, 
        task_id: uuid.UUID, 
        models: List[str],
        background_tasks: BackgroundTasks
    ) -> Experiment:
        task = await self.task_repository.get(task_id)
        if not task:
            raise ValueError(f"Task with id {task_id} not found")

        from config.models import MODEL_REGISTRY
        from core.exceptions import BadRequestException
        for model in models:
            model_info = MODEL_REGISTRY.get(model)
            if not model_info or not model_info.get("enabled"):
                raise BadRequestException(detail=f"Unsupported model: {model}")

        experiment = await self.experiment_repository.create(
            name=name,
            description=description,
            task_id=task_id,
        )
        
        for model in models:
            created_run = await self.evaluation_run_repository.create(
                task_id=task_id,
                world_id=task.world_id,
                experiment_id=experiment.id,
                model_name=model,
                status="pending",
            )
            
            # Queue background execution
            background_tasks.add_task(execute_run_in_background, created_run.id)
            
        return experiment
        
    async def get_experiment_summary(self, experiment_id: uuid.UUID) -> dict:
        experiment = await self.experiment_repository.get_with_runs(experiment_id)
        if not experiment:
            raise ValueError("Experiment not found")
            
        runs = experiment.evaluation_runs
        
        summary = {
            "highest_overall_score": None,
            "highest_accuracy": None,
            "best_groundedness": None,
            "best_retrieval": None,
            "lowest_hallucination": None,
            "fastest_model": None,
            "lowest_token_usage": None,
            "lowest_estimated_cost": None
        }
        
        if not runs:
            return {"experiment": experiment, "runs": runs, "summary": summary}
            
        completed_runs = [r for r in runs if r.status == "completed"]
        
        if completed_runs:
            summary["highest_overall_score"] = max(completed_runs, key=lambda r: (float(r.overall_score) if r.overall_score is not None else -1)).model_name
            summary["highest_accuracy"] = max(completed_runs, key=lambda r: (float(r.accuracy) if r.accuracy is not None else -1)).model_name
            summary["best_groundedness"] = max(completed_runs, key=lambda r: (float(r.groundedness) if r.groundedness is not None else -1)).model_name
            summary["best_retrieval"] = max(completed_runs, key=lambda r: (float(r.retrieval_score) if r.retrieval_score is not None else -1)).model_name
            
            summary["lowest_hallucination"] = min(completed_runs, key=lambda r: (float(r.hallucination_score) if r.hallucination_score is not None else 101)).model_name
            summary["fastest_model"] = min(completed_runs, key=lambda r: (r.latency_ms if r.latency_ms is not None else float('inf'))).model_name
            summary["lowest_token_usage"] = min(completed_runs, key=lambda r: (r.total_tokens if r.total_tokens is not None else float('inf'))).model_name
            
            summary["lowest_estimated_cost"] = min(completed_runs, key=lambda r: (r.total_tokens if r.total_tokens is not None else float('inf'))).model_name
            
        return {"experiment": experiment, "runs": runs, "summary": summary}
