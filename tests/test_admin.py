import pytest
from httpx import AsyncClient, Response


@pytest.mark.asyncio
async def test_create_user(
    client: AsyncClient,
    created_user: Response,
    admin_token: dict[str, str],
    user_token: dict[str, str],
):
    response = await client.post(
        "api/v1/admin/",
        json={"username": "theOne", "password": "notNeo", "repeat_password": "notNeo"},
        headers=user_token,
    )
    assert response.status_code == 403

    response = await client.post(
        "api/v1/admin/",
        json={"username": "admin", "password": "isBest", "repeat_password": "isBest"},
        headers=admin_token,
    )
    assert response.status_code == 403
    data = response.json()
    assert isinstance(data, dict)
    assert data.get("detail") == "Username already taken"

    response = await client.post(
        "api/v1/admin/",
        json={
            "username": "theOne",
            "password": "notNeo",
            "repeat_password": "NOTnotNeo",
        },
        headers=admin_token,
    )
    assert response.status_code == 409
    data = response.json()
    assert isinstance(data, dict)
    assert data.get("detail") == "Passwords don't match"
    assert created_user.status_code == 200

    data: dict[str, str | bool] = created_user.json()
    assert isinstance(data, dict)
    assert data.get("username") == "Luna"


@pytest.mark.asyncio
async def test_read_all_post(
    client: AsyncClient, admin_token: dict[str, str], user_token: dict[str, str]
):
    response = await client.get("/api/v1/admin/posts", headers=admin_token)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert "id" in data[0]
    assert "text" in data[0]
    assert "created_at" in data[0]
    assert "author_id" in data[0]
    assert "completed" in data[0]

    response = await client.get("/api/v1/admin/posts", headers=user_token)
    assert response.status_code == 403
    assert response.json()["detail"] == "User is not admin"


@pytest.mark.asyncio
async def test_update_users_role(
    client: AsyncClient, admin_token: dict[str, str], user_token: dict[str, str]
):
    user_info = {"username": "Aurora", "superuser": False}

    response = await client.put("/api/v1/admin/", json=user_info, headers=user_token)
    assert response.status_code == 403
    data = response.json()
    assert isinstance(data, dict)
    assert data["detail"] == "User is not admin"

    response = await client.put("/api/v1/admin/", json=user_info, headers=admin_token)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "username" in data
    assert "superuser" in data


@pytest.mark.asyncio
async def test_get_users_info_by_id(
    client: AsyncClient, admin_token: dict[str, str], user_token: dict[str, str]
):
    response = await client.get("/api/v1/admin/id/2", headers=user_token)
    assert response.status_code == 403
    data = response.json()
    assert isinstance(data, dict)
    assert data["detail"] == "User is not admin"

    response = await client.get("/api/v1/admin/id/2", headers=admin_token)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "id" in data
    assert "username" in data
    assert "superuser" in data
    assert "is_active" in data

    response = await client.get("/api/v1/admin/id/999999", headers=admin_token)
    assert response.status_code == 404
    data = response.json()
    assert isinstance(data, dict)
    assert data["detail"] == "User's id not found"


@pytest.mark.asyncio
async def test_get_users_info_by_name(
    client: AsyncClient, admin_token: dict[str, str], user_token: dict[str, str]
):
    response = await client.get("/api/v1/admin/username/Aurora", headers=user_token)
    assert response.status_code == 403
    data = response.json()
    assert isinstance(data, dict)
    assert data["detail"] == "User is not admin"

    response = await client.get("/api/v1/admin/username/Aurora", headers=admin_token)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "id" in data
    assert "username" in data
    assert "superuser" in data
    assert "is_active" in data

    response = await client.get("/api/v1/admin/username/a", headers=admin_token)
    assert response.status_code == 404
    data = response.json()
    assert isinstance(data, dict)
    assert data["detail"] == "Username not found"


@pytest.mark.asyncio
async def test_delete_user_by_admin(
    client: AsyncClient,
    created_user: Response,
    admin_token: dict[str, str],
    user_token: dict[str, str],
):
    data: dict[str, str | bool] = created_user.json()
    assert created_user.status_code == 200
    assert isinstance(data, dict)
    assert data.get("username") == "Luna"

    response = await client.request("DELETE", "/api/v1/admin/Luna")
    assert response.status_code == 401
    data = response.json()
    assert isinstance(data, dict)
    assert data["detail"] == "Not authenticated"

    response = await client.request("DELETE", "/api/v1/admin/Luna", headers=user_token)
    assert response.status_code == 403
    data = response.json()
    assert isinstance(data, dict)
    assert data["detail"] == "User is not admin"

    response = await client.request("DELETE", "/api/v1/admin/Luna", headers=admin_token)
    assert response.status_code == 204
