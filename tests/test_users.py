import pytest
from httpx import AsyncClient, Response


@pytest.mark.asyncio
async def test_register_user(
    client: AsyncClient,
    created_user: Response,
    user_token: dict[str, str],
):
    response = await client.post(
        "api/v1/users/register",
        json={
            "username": "theOne",
            "password": "notNeo",
            "repeat_password": "notNeo",
        },
        headers=user_token,
    )
    assert response.status_code == 403
    data = response.json()
    assert isinstance(data, dict)
    assert data.get("detail") == "User is already logged in"

    response = await client.post(
        "api/v1/users/register",
        json={
            "username": "admin",
            "password": "notNeo",
            "repeat_password": "notNotNeo",
        },
    )
    assert response.status_code == 409
    data = response.json()
    assert isinstance(data, dict)
    assert data.get("detail") == "Username already taken"

    response = await client.post(
        "api/v1/users/register",
        json={
            "username": "theOne",
            "password": "notNeo",
            "repeat_password": "notNotNeo",
        },
    )
    data = response.json()
    assert response.status_code == 409
    assert data.get("detail") == "Passwords don't match"
    assert created_user.status_code == 200
    data: dict[str, str | bool] = created_user.json()
    assert isinstance(data, dict)
    assert data.get("username") == "Luna"


@pytest.mark.asyncio
async def test_login_user(client: AsyncClient, created_user: Response):
    _ = created_user
    response = await client.post(
        "/api/v1/users/login", data={"username": "Luna", "password": "wrongPass"}
    )
    assert response.status_code == 401
    data_: dict[str, str] = response.json()
    assert isinstance(data_, dict)
    assert data_["detail"] == "Username or password is incorrect"

    response = await client.post(
        "/api/v1/users/login", data={"username": "Luna", "password": "vulpkanin"}
    )
    assert response.status_code == 200
    data: dict[str, str] = response.json()
    assert isinstance(data, dict)
    assert "access_token" in data
    assert data.get("token_type") == "bearer"


@pytest.mark.asyncio
async def test_delete_user_by_user(client: AsyncClient, created_user: Response):
    _ = created_user
    response = await client.post(
        "/api/v1/users/login", data={"username": "Luna", "password": "vulpkanin"}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    user_token = {"Authorization": f"Bearer {token}"}
    response = await client.request(
        "DELETE", "/api/v1/users/delete", headers=user_token
    )
    assert response.status_code == 200
    data = response.json()
    assert data.get("username") == "Luna"
    assert not data.get("is_active")


@pytest.mark.asyncio
async def test_logout_user(client: AsyncClient, user_token: dict[str, str]):
    response = await client.post("/api/v1/users/logout")
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Not authenticated"

    response = await client.post("/api/v1/users/logout", headers=user_token)
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_edit_users_info_by_user(
    client: AsyncClient, created_user: Response, user_token: dict[str, str]
):
    _ = created_user
    user_login = {"username": "Luna", "password": "vulpkanin"}
    user_update_info = {
        "username": "Luna",
        "password": "newPass",
        "repeat_password": "newPass",
    }

    response = await client.patch("/api/v1/users/", json=user_update_info)
    assert response.status_code == 401
    data = response.json()
    assert isinstance(data, dict)
    assert data["detail"] == "Not authenticated"

    response = await client.patch(
        "/api/v1/users/", json=user_update_info, headers=user_token
    )
    assert response.status_code == 403
    data = response.json()
    assert isinstance(data, dict)
    assert data["detail"] == "User is not authorized"

    response = await client.post("/api/v1/users/login", data=user_login)
    assert response.status_code == 200
    token = response.json()["access_token"]
    user_token = {"Authorization": f"Bearer {token}"}

    response = await client.patch(
        "/api/v1/users/", json=user_update_info, headers=user_token
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "username" in data
    assert "is_active" in data
