import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from models.world import World


@pytest.fixture
async def sample_world(db_session: AsyncSession) -> World:
    world = World(name="Test World", description="A test world for documents")
    db_session.add(world)
    await db_session.commit()
    await db_session.refresh(world)
    return world


@pytest.mark.asyncio
async def test_create_document(async_client: AsyncClient, sample_world: World):
    response = await async_client.post(
        "/api/v1/documents",
        json={
            "world_id": str(sample_world.id),
            "filename": "test_document.pdf",
            "document_type": "pdf",
            "department": "Engineering"
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["filename"] == "test_document.pdf"
    assert data["world_id"] == str(sample_world.id)
    assert "id" in data


@pytest.mark.asyncio
async def test_create_document_invalid_world(async_client: AsyncClient):
    response = await async_client.post(
        "/api/v1/documents",
        json={
            "world_id": str(uuid.uuid4()),
            "filename": "invalid_world.txt"
        },
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "World not found."


@pytest.mark.asyncio
async def test_list_documents(async_client: AsyncClient, sample_world: World):
    await async_client.post(
        "/api/v1/documents",
        json={"world_id": str(sample_world.id), "filename": "doc1.txt"}
    )
    
    response = await async_client.get("/api/v1/documents")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["filename"] == "doc1.txt"


@pytest.mark.asyncio
async def test_list_documents_by_world(async_client: AsyncClient, sample_world: World, db_session: AsyncSession):
    # Create another world
    world2 = World(name="World 2")
    db_session.add(world2)
    await db_session.commit()
    await db_session.refresh(world2)

    await async_client.post(
        "/api/v1/documents",
        json={"world_id": str(sample_world.id), "filename": "world1_doc.txt"}
    )
    await async_client.post(
        "/api/v1/documents",
        json={"world_id": str(world2.id), "filename": "world2_doc.txt"}
    )
    
    response = await async_client.get(f"/api/v1/documents?world_id={sample_world.id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["filename"] == "world1_doc.txt"


@pytest.mark.asyncio
async def test_get_document(async_client: AsyncClient, sample_world: World):
    create_response = await async_client.post(
        "/api/v1/documents",
        json={"world_id": str(sample_world.id), "filename": "get_me.txt"}
    )
    doc_id = create_response.json()["id"]

    response = await async_client.get(f"/api/v1/documents/{doc_id}")
    assert response.status_code == 200
    assert response.json()["id"] == doc_id


@pytest.mark.asyncio
async def test_get_document_not_found(async_client: AsyncClient):
    response = await async_client.get(f"/api/v1/documents/{uuid.uuid4()}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_document(async_client: AsyncClient, sample_world: World):
    create_response = await async_client.post(
        "/api/v1/documents",
        json={"world_id": str(sample_world.id), "filename": "delete_me.txt"}
    )
    doc_id = create_response.json()["id"]

    delete_response = await async_client.delete(f"/api/v1/documents/{doc_id}")
    assert delete_response.status_code == 204

    get_response = await async_client.get(f"/api/v1/documents/{doc_id}")
    assert get_response.status_code == 404
