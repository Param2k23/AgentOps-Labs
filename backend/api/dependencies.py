from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from config.settings import Settings, get_settings
from core.database import get_db
from repositories.world import WorldRepository
from repositories.document import DocumentRepository
from repositories.task import TaskRepository
from repositories.evaluation_run import EvaluationRunRepository
from repositories.document_chunk import DocumentChunkRepository
from services.world import WorldService
from services.document import DocumentService
from services.task import TaskService
from services.evaluation_run import EvaluationRunService
from services.evaluation_engine import EvaluationEngineService
from services.embedding import EmbeddingService
from services.retrieval import RetrievalService
from services.llm import LLMService, GeminiProvider, ProviderInterface


def get_app_settings() -> Settings:
    return get_settings()

def get_llm_service() -> LLMService:
    """Provide a singleton LLMService instance based on config."""
    settings = get_settings()
    
    provider: ProviderInterface
    if settings.llm_provider.lower() == "gemini":
        provider = GeminiProvider(api_key=settings.gemini_api_key)
    else:
        # Fallback to Gemini for now
        provider = GeminiProvider(api_key=settings.gemini_api_key)
        
    return LLMService(
        provider=provider,
        model=settings.gemini_model,
        timeout=settings.llm_timeout,
        temperature=settings.llm_temperature
    )

def get_embedding_service() -> EmbeddingService:
    """Provide a singleton EmbeddingService instance."""
    # Instantiating the service (it lazy-loads the model)
    return EmbeddingService()

def get_retrieval_service(
    db: AsyncSession = Depends(get_db),
    embedding_service: EmbeddingService = Depends(get_embedding_service)
) -> RetrievalService:
    """Provide a RetrievalService instance with injected dependencies."""
    document_repo = DocumentRepository(session=db)
    document_chunk_repo = DocumentChunkRepository(session=db)
    task_repo = TaskRepository(session=db)
    return RetrievalService(
        document_repository=document_repo,
        document_chunk_repository=document_chunk_repo,
        task_repository=task_repo,
        embedding_service=embedding_service,
    )


def get_world_service(db: AsyncSession = Depends(get_db)) -> WorldService:
    """Provide a WorldService instance with injected dependencies."""
    repository = WorldRepository(session=db)
    return WorldService(repository=repository)


def get_document_service(db: AsyncSession = Depends(get_db)) -> DocumentService:
    """Provide a DocumentService instance with injected dependencies."""
    document_repo = DocumentRepository(session=db)
    world_repo = WorldRepository(session=db)
    return DocumentService(document_repository=document_repo, world_repository=world_repo)


def get_task_service(db: AsyncSession = Depends(get_db)) -> TaskService:
    """Provide a TaskService instance with injected dependencies."""
    task_repo = TaskRepository(session=db)
    document_repo = DocumentRepository(session=db)
    world_repo = WorldRepository(session=db)
    return TaskService(task_repository=task_repo, document_repository=document_repo, world_repository=world_repo)


def get_evaluation_run_service(db: AsyncSession = Depends(get_db)) -> EvaluationRunService:
    """Provide an EvaluationRunService instance with injected dependencies."""
    eval_run_repo = EvaluationRunRepository(session=db)
    task_repo = TaskRepository(session=db)
    world_repo = WorldRepository(session=db)
    return EvaluationRunService(
        evaluation_run_repository=eval_run_repo,
        task_repository=task_repo,
        world_repository=world_repo,
    )

def get_evaluation_engine_service(
    db: AsyncSession = Depends(get_db),
    retrieval_service: RetrievalService = Depends(get_retrieval_service),
    llm_service: LLMService = Depends(get_llm_service),
) -> EvaluationEngineService:
    """Provide an EvaluationEngineService instance."""
    eval_run_repo = EvaluationRunRepository(session=db)
    task_repo = TaskRepository(session=db)
    return EvaluationEngineService(
        evaluation_run_repository=eval_run_repo,
        task_repository=task_repo,
        retrieval_service=retrieval_service,
        llm_service=llm_service,
    )
