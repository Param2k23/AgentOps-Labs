from typing import Any, Sequence
from uuid import UUID

from core.exceptions import NotFoundException
from repositories.task import TaskRepository
from repositories.document import DocumentRepository
from repositories.world import WorldRepository
from schemas.task import TaskCreate, TaskResponse


class TaskService:
    """Service layer for Task entities."""

    def __init__(
        self,
        task_repository: TaskRepository,
        document_repository: DocumentRepository,
        world_repository: WorldRepository,
    ):
        self.task_repository = task_repository
        self.document_repository = document_repository
        self.world_repository = world_repository

    async def create_task(self, data: TaskCreate) -> TaskResponse:
        """Create a new task. Validates that the world and document exist."""
        world = await self.world_repository.get(data.world_id)
        if not world:
            raise NotFoundException(detail="World not found.")
            
        document = await self.document_repository.get(data.document_id)
        if not document:
            raise NotFoundException(detail="Document not found.")
        
        task = await self.task_repository.create(**data.model_dump())
        return TaskResponse.model_validate(task)

    async def get_task(self, task_id: UUID) -> TaskResponse:
        """Retrieve a task by its ID."""
        task = await self.task_repository.get(task_id)
        if not task:
            raise NotFoundException(detail="Task not found.")
        return TaskResponse.model_validate(task)

    async def get_all_tasks(self, skip: int = 0, limit: int = 100) -> Sequence[TaskResponse]:
        """Retrieve all tasks."""
        tasks = await self.task_repository.get_all(skip=skip, limit=limit)
        return [TaskResponse.model_validate(t) for t in tasks]

    async def get_tasks_by_world(self, world_id: UUID, skip: int = 0, limit: int = 100) -> Sequence[TaskResponse]:
        """Retrieve tasks by world ID."""
        world = await self.world_repository.get(world_id)
        if not world:
            raise NotFoundException(detail="World not found.")
            
        tasks = await self.task_repository.get_by_world_id(world_id, skip=skip, limit=limit)
        return [TaskResponse.model_validate(t) for t in tasks]

    async def delete_task(self, task_id: UUID) -> None:
        """Delete a task by its ID."""
        deleted = await self.task_repository.delete(task_id)
        if not deleted:
            raise NotFoundException(detail="Task not found.")
