import pytest

@pytest.mark.asyncio
async def test_create_post(client, admin_token, created_post):
    assert created_post.status_code == 200
    data = created_post.json()
    assert isinstance(data, dict)
    assert 'id' in data
    assert 'text' in data
    assert 'created_at' in data

@pytest.mark.asyncio
async def test_show_latest_posts(client, user_token):
    response = await client.get('/api/v1/posts/', headers=user_token)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert 'text' in data[0]

@pytest.mark.asyncio
async def test_read_todays_post(client, user_token):
    response = await client.get('/api/v1/posts/today', headers=user_token)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert 'text' in data

@pytest.mark.asyncio
async def test_delete_post(client, created_post, admin_token, user_token):
    post_id = created_post.json()['id']
    response = await client.delete(f'/api/v1/posts/{post_id}', headers=user_token)
    assert response.status_code == 403
    response = await client.delete(f'/api/v1/posts/{post_id}', headers=admin_token)
    assert response.status_code == 204
    response = await client.delete(f'/api/v1/posts/{post_id}', headers=admin_token )
    assert response.status_code == 404