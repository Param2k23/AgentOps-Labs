import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_world(async_client: AsyncClient) -> None:
    payload = {
        "name": "Test World",
        "description": "A testing world",
        "industry": "Software",
    }
    response = await async_client.post("/api/v1/worlds", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test World"
    assert data["description"] == "A testing world"
    assert data["industry"] == "Software"
    assert data["status"] == "active"
    assert "id" in data


@pytest.mark.asyncio
async def test_create_world_validation_error(async_client: AsyncClient) -> None:
    payload = {
        "name": "",  # Too short
    }
    response = await async_client.post("/api/v1/worlds", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_worlds(async_client: AsyncClient) -> None:
    # Create a world
    payload = {"name": "World 1"}
    await async_client.post("/api/v1/worlds", json=payload)

    response = await async_client.get("/api/v1/worlds")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["name"] == "World 1"


@pytest.mark.asyncio
async def test_get_world(async_client: AsyncClient) -> None:
    payload = {"name": "World 2"}
    create_response = await async_client.post("/api/v1/worlds", json=payload)
    world_id = create_response.json()["id"]

    response = await async_client.get(f"/api/v1/worlds/{world_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "World 2"


@pytest.mark.asyncio
async def test_get_world_not_found(async_client: AsyncClient) -> None:
    import uuid
    random_id = str(uuid.uuid4())
    response = await async_client.get(f"/api/v1/worlds/{random_id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_world(async_client: AsyncClient) -> None:
    payload = {"name": "World to delete"}
    create_response = await async_client.post("/api/v1/worlds", json=payload)
    world_id = create_response.json()["id"]

    response = await async_client.delete(f"/api/v1/worlds/{world_id}")
    assert response.status_code == 204

    # Verify deleted
    get_response = await async_client.get(f"/api/v1/worlds/{world_id}")
    assert get_response.status_code == 404
