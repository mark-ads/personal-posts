from collections.abc import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient, Response

from src.core.config import settings
from src.main import app

ADMIN_PASS = settings.ADMIN_PASS


@pytest_asyncio.fixture(scope="session")
async def client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


@pytest_asyncio.fixture(scope="session")
async def admin_token(client: AsyncClient) -> AsyncGenerator[dict[str, str], None]:
    response = await client.post(
        "/api/v1/users/login", data={"username": "admin", "password": ADMIN_PASS}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    yield headers


@pytest_asyncio.fixture(scope="session")
async def user_token(client: AsyncClient) -> AsyncGenerator[dict[str, str], None]:
    response = await client.post(
        "/api/v1/users/login", data={"username": "Aurora", "password": ADMIN_PASS}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    header = {"Authorization": f"Bearer {token}"}
    yield header


@pytest_asyncio.fixture(scope="function")
async def created_user(
    client: AsyncClient, admin_token: dict[str, str]
) -> AsyncGenerator[Response, None]:
    user_data = {"username": "Luna", "password": "vulpkanin"}
    response = await client.post("/api/v1/users/", json=user_data, headers=admin_token)
    yield response
    await client.request(
        "DELETE", "/api/v1/users/", json={"username": "Luna"}, headers=admin_token
    )


@pytest_asyncio.fixture(scope="function")
async def created_admin_post(
    client: AsyncClient, admin_token: dict[str, str]
) -> AsyncGenerator[Response, None]:
    post_data = {"text": "Testing test text"}
    response = await client.post("/api/v1/posts/", json=post_data, headers=admin_token)
    post_id = response.json()["id"]
    yield response
    await client.delete(f"/api/v1/posts/{post_id}", headers=admin_token)


@pytest_asyncio.fixture(scope="function")
async def created_user_post(
    client: AsyncClient, user_token: dict[str, str]
) -> AsyncGenerator[Response, None]:
    post_data = {"text": "Testing test text"}
    response = await client.post("/api/v1/posts/", json=post_data, headers=user_token)
    post_id = response.json()["id"]
    yield response
    await client.delete(f"/api/v1/posts/{post_id}", headers=user_token)

