from typing import Any, Sequence
from uuid import UUID

from core.exceptions import NotFoundException
from repositories.evaluation_run import EvaluationRunRepository
from repositories.task import TaskRepository
from repositories.world import WorldRepository
from schemas.evaluation_run import EvaluationRunCreate, EvaluationRunResponse


class EvaluationRunService:
    """Service layer for EvaluationRun entities."""

    def __init__(
        self,
        evaluation_run_repository: EvaluationRunRepository,
        task_repository: TaskRepository,
        world_repository: WorldRepository,
    ):
        self.evaluation_run_repository = evaluation_run_repository
        self.task_repository = task_repository
        self.world_repository = world_repository

    async def create_evaluation_run(self, data: EvaluationRunCreate) -> EvaluationRunResponse:
        """Create a new evaluation run. Validates that the task exists."""
        task = await self.task_repository.get(data.task_id)
        if not task:
            raise NotFoundException(detail="Task not found.")
            
        world = await self.world_repository.get(data.world_id)
        if not world:
            raise NotFoundException(detail="World not found.")
        
        # We could also validate that task.world_id == data.world_id,
        # but relying on what's passed for now based on schema.
        if task.world_id != data.world_id:
            raise NotFoundException(detail="Task does not belong to the specified world.")
        
        eval_run = await self.evaluation_run_repository.create(**data.model_dump())
        return EvaluationRunResponse.model_validate(eval_run)

    async def get_evaluation_run(self, eval_run_id: UUID) -> EvaluationRunResponse:
        """Retrieve an evaluation run by its ID."""
        eval_run = await self.evaluation_run_repository.get(eval_run_id)
        if not eval_run:
            raise NotFoundException(detail="Evaluation run not found.")
        return EvaluationRunResponse.model_validate(eval_run)

    async def get_all_evaluation_runs(self, skip: int = 0, limit: int = 100) -> Sequence[EvaluationRunResponse]:
        """Retrieve all evaluation runs."""
        eval_runs = await self.evaluation_run_repository.get_all(skip=skip, limit=limit)
        return [EvaluationRunResponse.model_validate(er) for er in eval_runs]

    async def get_evaluation_runs_by_world(self, world_id: UUID, skip: int = 0, limit: int = 100) -> Sequence[EvaluationRunResponse]:
        """Retrieve evaluation runs by world ID."""
        world = await self.world_repository.get(world_id)
        if not world:
            raise NotFoundException(detail="World not found.")
            
        eval_runs = await self.evaluation_run_repository.get_by_world_id(world_id, skip=skip, limit=limit)
        return [EvaluationRunResponse.model_validate(er) for er in eval_runs]

    async def delete_evaluation_run(self, eval_run_id: UUID) -> None:
        """Delete an evaluation run by its ID."""
        deleted = await self.evaluation_run_repository.delete(eval_run_id)
        if not deleted:
            raise NotFoundException(detail="Evaluation run not found.")
