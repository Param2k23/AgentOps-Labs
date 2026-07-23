import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from models.world import World
from models.document import Document
from models.task import Task


@pytest.fixture
async def sample_world(db_session: AsyncSession) -> World:
    world = World(name="Test World", description="A test world for eval runs")
    db_session.add(world)
    await db_session.commit()
    await db_session.refresh(world)
    return world


@pytest.fixture
async def sample_document(db_session: AsyncSession, sample_world: World) -> Document:
    document = Document(world_id=sample_world.id, filename="test_doc.pdf")
    db_session.add(document)
    await db_session.commit()
    await db_session.refresh(document)
    return document


@pytest.fixture
async def sample_task(db_session: AsyncSession, sample_world: World, sample_document: Document) -> Task:
    task = Task(world_id=sample_world.id, document_id=sample_document.id, title="Test Task")
    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)
    return task


@pytest.mark.asyncio
async def test_create_evaluation_run(async_client: AsyncClient, sample_world: World, sample_task: Task):
    response = await async_client.post(
        "/api/v1/evaluation-runs",
        json={
            "task_id": str(sample_task.id),
            "world_id": str(sample_world.id),
            "model_name": "gpt-4o"
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["task_id"] == str(sample_task.id)
    assert data["world_id"] == str(sample_world.id)
    assert data["model_name"] == "gpt-4o"
    assert data["status"] == "pending"
    assert "id" in data


@pytest.mark.asyncio
async def test_create_evaluation_run_invalid_task(async_client: AsyncClient, sample_world: World):
    response = await async_client.post(
        "/api/v1/evaluation-runs",
        json={
            "task_id": str(uuid.uuid4()),
            "world_id": str(sample_world.id),
            "model_name": "gpt-4o"
        },
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found."


@pytest.mark.asyncio
async def test_list_evaluation_runs(async_client: AsyncClient, sample_world: World, sample_task: Task):
    await async_client.post(
        "/api/v1/evaluation-runs",
        json={
            "task_id": str(sample_task.id),
            "world_id": str(sample_world.id),
            "model_name": "gpt-4o"
        }
    )
    
    response = await async_client.get("/api/v1/evaluation-runs")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["model_name"] == "gpt-4o"


@pytest.mark.asyncio
async def test_get_evaluation_run(async_client: AsyncClient, sample_world: World, sample_task: Task):
    create_response = await async_client.post(
        "/api/v1/evaluation-runs",
        json={
            "task_id": str(sample_task.id),
            "world_id": str(sample_world.id)
        }
    )
    eval_id = create_response.json()["id"]

    response = await async_client.get(f"/api/v1/evaluation-runs/{eval_id}")
    assert response.status_code == 200
    assert response.json()["id"] == eval_id


@pytest.mark.asyncio
async def test_delete_evaluation_run(async_client: AsyncClient, sample_world: World, sample_task: Task):
    create_response = await async_client.post(
        "/api/v1/evaluation-runs",
        json={
            "task_id": str(sample_task.id),
            "world_id": str(sample_world.id)
        }
    )
    eval_id = create_response.json()["id"]

    delete_response = await async_client.delete(f"/api/v1/evaluation-runs/{eval_id}")
    assert delete_response.status_code == 204

    get_response = await async_client.get(f"/api/v1/evaluation-runs/{eval_id}")
    assert get_response.status_code == 404
