import pytest
from httpx import AsyncClient, Response


@pytest.mark.asyncio
async def test_create_post(created_user_post: Response):
    assert created_user_post.status_code == 200
    data = created_user_post.json()
    assert isinstance(data, dict)
    assert "id" in data
    assert "text" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_read_selected_post(
    client: AsyncClient,
    created_user_post: Response,
    created_admin_post: Response,
    user_token: dict[str, str],
):
    post_id = created_admin_post.json()["id"]
    response = await client.get(f"/api/v1/posts/{post_id}", headers=user_token)
    assert response.status_code == 403
    post_id = created_user_post.json()["id"]
    response = await client.get(f"/api/v1/posts/{post_id}", headers=user_token)
    assert response.status_code == 200
    data = response.json()
    assert "text" in data
    assert "created_at" in data
    assert "completed" in data


@pytest.mark.asyncio
async def test_read_users_posts(client: AsyncClient, user_token: dict[str, str]):
    response: Response = await client.get("/api/v1/posts/", headers=user_token)
    assert response.status_code == 200
    data: list[dict[str, str | int | bool]] = response.json()
    assert isinstance(data, list)
    assert "text" in data[0]
    assert "created_at" in data[0]
    assert "completed" in data[0]
    assert data[0].get("id") != "1"


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
async def test_change_post(
    client: AsyncClient,
    user_token: dict[str, str],
    admin_token: dict[str, str],
    created_admin_post: Response,
):
    origin_text = created_admin_post.json()["text"]
    post_data = {"text": "Testing PUT method to change post"}
    post_id = created_admin_post.json()["id"]
    response = await client.put(
        f"/api/v1/posts/{post_id}", json=post_data, headers=user_token
    )
    assert response.status_code == 403
    response = await client.put(
        f"/api/v1/posts/{post_id}", json=post_data, headers=admin_token
    )
    assert response.status_code == 200
    assert response.json()["text"] != origin_text


@pytest.mark.asyncio
async def test_check_completed(
    client: AsyncClient,
    created_admin_post: Response,
    created_user_post: Response,
    user_token: dict[str, str],
):
    post_id = created_admin_post.json()["id"]
    post_data = {"completed": True}
    response = await client.patch(
        f"/api/v1/posts/{post_id}/completed", json=post_data, headers=user_token
    )
    assert response.status_code == 403
    post_id = created_user_post.json()["id"]
    response = await client.patch(
        f"/api/v1/posts/{post_id}/completed", json=post_data, headers=user_token
    )
    assert response.status_code == 200
    assert response.json()["completed"]


@pytest.mark.asyncio
async def test_delete_post(
    client: AsyncClient,
    created_admin_post: Response,
    created_user_post: Response,
    admin_token: dict[str, str],
    user_token: dict[str, str],
):
    post_id = created_user_post.json()["id"]
    response = await client.delete(f"/api/v1/posts/{post_id}", headers=user_token)
    assert response.status_code == 204
    response = await client.delete(f"/api/v1/posts/{post_id}", headers=user_token)
    assert response.status_code == 404
    post_id = created_admin_post.json()["id"]
    response = await client.delete(f"/api/v1/posts/{post_id}", headers=user_token)
    assert response.status_code == 403
    response = await client.delete(f"/api/v1/posts/{post_id}", headers=admin_token)
    assert response.status_code == 204
    response = await client.delete(f"/api/v1/posts/{post_id}", headers=admin_token)
    assert response.status_code == 404

