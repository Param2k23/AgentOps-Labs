import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from models.world import World
from models.document import Document


@pytest.fixture
async def sample_world(db_session: AsyncSession) -> World:
    world = World(name="Test World", description="A test world for tasks")
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


@pytest.mark.asyncio
async def test_create_task(async_client: AsyncClient, sample_world: World, sample_document: Document):
    response = await async_client.post(
        "/api/v1/tasks",
        json={
            "world_id": str(sample_world.id),
            "document_id": str(sample_document.id),
            "title": "Analyze Document",
            "difficulty": "Easy",
            "department": "Engineering"
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Analyze Document"
    assert data["world_id"] == str(sample_world.id)
    assert data["document_id"] == str(sample_document.id)
    assert "id" in data


@pytest.mark.asyncio
async def test_create_task_invalid_document(async_client: AsyncClient, sample_world: World):
    response = await async_client.post(
        "/api/v1/tasks",
        json={
            "world_id": str(sample_world.id),
            "document_id": str(uuid.uuid4()),
            "title": "Invalid Document Task"
        },
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Document not found."


@pytest.mark.asyncio
async def test_create_task_invalid_world(async_client: AsyncClient, sample_document: Document):
    response = await async_client.post(
        "/api/v1/tasks",
        json={
            "world_id": str(uuid.uuid4()),
            "document_id": str(sample_document.id),
            "title": "Invalid World Task"
        },
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "World not found."


@pytest.mark.asyncio
async def test_list_tasks(async_client: AsyncClient, sample_world: World, sample_document: Document):
    await async_client.post(
        "/api/v1/tasks",
        json={
            "world_id": str(sample_world.id),
            "document_id": str(sample_document.id),
            "title": "task1"
        }
    )
    
    response = await async_client.get("/api/v1/tasks")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["title"] == "task1"


@pytest.mark.asyncio
async def test_get_task(async_client: AsyncClient, sample_world: World, sample_document: Document):
    create_response = await async_client.post(
        "/api/v1/tasks",
        json={
            "world_id": str(sample_world.id),
            "document_id": str(sample_document.id),
            "title": "get_me"
        }
    )
    task_id = create_response.json()["id"]

    response = await async_client.get(f"/api/v1/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json()["id"] == task_id


@pytest.mark.asyncio
async def test_get_task_not_found(async_client: AsyncClient):
    response = await async_client.get(f"/api/v1/tasks/{uuid.uuid4()}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_task(async_client: AsyncClient, sample_world: World, sample_document: Document):
    create_response = await async_client.post(
        "/api/v1/tasks",
        json={
            "world_id": str(sample_world.id),
            "document_id": str(sample_document.id),
            "title": "delete_me"
        }
    )
    task_id = create_response.json()["id"]

    delete_response = await async_client.delete(f"/api/v1/tasks/{task_id}")
    assert delete_response.status_code == 204

    get_response = await async_client.get(f"/api/v1/tasks/{task_id}")
    assert get_response.status_code == 404
