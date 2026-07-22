"""
Unit tests for SQLAlchemy models and Pydantic schemas.

Verifies:
- Creation of World, Document, Task, and EvaluationRun entities
- UUID primary keys and timestamps
- Foreign key constraints and relationships
- Pydantic schema validation and serialization
"""

import uuid
from datetime import datetime

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Document, EvaluationRun, Task, World
from schemas import (
    DocumentCreate,
    DocumentResponse,
    EvaluationRunCreate,
    EvaluationRunResponse,
    TaskCreate,
    TaskResponse,
    WorldCreate,
    WorldResponse,
)


@pytest.mark.asyncio
async def test_create_world(db_session: AsyncSession) -> None:
    """Test creating a World ORM model and converting to/from Pydantic schema."""
    world_in = WorldCreate(
        name="TechNova",
        description="Enterprise Financial World",
        industry="Finance",
        metadata={"region": "us-east"},
    )

    world = World(
        name=world_in.name,
        description=world_in.description,
        industry=world_in.industry,
        metadata_=world_in.metadata,
    )
    db_session.add(world)
    await db_session.commit()
    await db_session.refresh(world)

    assert isinstance(world.id, uuid.UUID)
    assert world.name == "TechNova"
    assert world.status == "active"
    assert isinstance(world.created_at, datetime)

    # Test Pydantic schema serialization from ORM object
    schema_res = WorldResponse.model_validate(world)
    assert schema_res.id == world.id
    assert schema_res.name == "TechNova"
    assert schema_res.metadata == {"region": "us-east"}


@pytest.mark.asyncio
async def test_world_document_relationship(db_session: AsyncSession) -> None:
    """Test 1:N relationship between World and Documents."""
    world = World(name="LegalCorp", industry="Legal")
    db_session.add(world)
    await db_session.commit()

    doc1 = Document(
        world_id=world.id,
        filename="contract.pdf",
        document_type="pdf",
        department="Legal",
        file_size=1024,
    )
    doc2 = Document(
        world_id=world.id,
        filename="policy.docx",
        document_type="docx",
        department="HR",
        file_size=2048,
    )
    db_session.add_all([doc1, doc2])
    await db_session.commit()
    await db_session.refresh(world, ["documents"])

    assert len(world.documents) == 2
    filenames = {d.filename for d in world.documents}
    assert filenames == {"contract.pdf", "policy.docx"}

    # Test Pydantic schema conversion
    doc_res = DocumentResponse.model_validate(doc1)
    assert doc_res.id == doc1.id
    assert doc_res.world_id == world.id
    assert doc_res.filename == "contract.pdf"


@pytest.mark.asyncio
async def test_world_task_evaluation_relationship(db_session: AsyncSession) -> None:
    """Test World -> Task -> EvaluationRun relationships and cascaded queries."""
    world = World(name="RetailHub", industry="Retail")
    db_session.add(world)
    await db_session.commit()

    task = Task(
        world_id=world.id,
        title="Inventory Audit",
        description="Verify Q3 stock levels",
        difficulty="Hard",
        department="Operations",
        ground_truth="Pass",
    )
    db_session.add(task)
    await db_session.commit()

    eval_run = EvaluationRun(
        task_id=task.id,
        world_id=world.id,
        model_name="gpt-4o",
        status="completed",
        accuracy=95.5,
        overall_score=92.0,
    )
    db_session.add(eval_run)
    await db_session.commit()
    await db_session.refresh(task, ["evaluation_runs"])

    assert len(task.evaluation_runs) == 1
    assert task.evaluation_runs[0].model_name == "gpt-4o"
    assert task.evaluation_runs[0].accuracy == 95.5

    # Test Pydantic schemas
    task_res = TaskResponse.model_validate(task)
    assert task_res.id == task.id
    assert task_res.title == "Inventory Audit"

    eval_res = EvaluationRunResponse.model_validate(eval_run)
    assert eval_res.id == eval_run.id
    assert eval_res.accuracy == 95.5
    assert eval_res.status == "completed"
