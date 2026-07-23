import random
from datetime import datetime, timezone
from uuid import UUID

from core.exceptions import NotFoundException, BadRequestException
from models.evaluation_run import EvaluationRun
from repositories.evaluation_run import EvaluationRunRepository
from repositories.task import TaskRepository
from schemas.evaluation_run import EvaluationRunResponse

class EvaluationEngineService:
    """Service responsible for executing EvaluationRuns."""

    def __init__(
        self,
        evaluation_run_repository: EvaluationRunRepository,
        task_repository: TaskRepository,
    ):
        self.evaluation_run_repository = evaluation_run_repository
        self.task_repository = task_repository

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
            
        document = task.document
        doc_text = document.extracted_text if document and document.extracted_text else "No document attached."

        # 3. Generate Model Response (Mock implementation)
        # In the future, this will call the actual LLM integration.
        generated_response = (
            f"Mock generated response for task: {task.title}.\n"
            f"Based on document content (snippet): {doc_text[:100]}...\n"
            "This is a placeholder for the actual LLM generation."
        )

        # 4. Evaluate the response against task's expected_output/rubric (Mock implementation)
        # Using a deterministic random score based on string lengths for consistent behavior
        base_seed = len(generated_response) + len(task.ground_truth or "") + len(task.rubric or "")
        random.seed(base_seed)
        
        accuracy = round(random.uniform(70.0, 100.0), 2)
        groundedness = round(random.uniform(70.0, 100.0), 2)
        citation_score = round(random.uniform(60.0, 100.0), 2)
        retrieval_score = round(random.uniform(60.0, 100.0), 2)
        hallucination_score = round(random.uniform(0.0, 15.0), 2)
        tool_success = round(random.uniform(80.0, 100.0), 2)
        
        overall_score = round((accuracy + groundedness + citation_score) / 3, 2)
        
        feedback = "Mock evaluation completed successfully."

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
            feedback=feedback
        )

        return EvaluationRunResponse.model_validate(eval_run_model)
