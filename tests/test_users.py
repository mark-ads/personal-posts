import pytest

@pytest.mark.asyncio
async def test_create_user(client, created_user, admin_token, user_token):
    response = await client.post('api/v1/users/', json={'username': 'theOne', 'password': 'notNeo'}, headers=user_token)
    assert response.status_code == 403
    response = await client.post('api/v1/users/', json={'username': 'admin', 'password': 'isBest'}, headers=admin_token)
    assert response.status_code == 403
    data = response.json()
    assert data.get('detail') == 'Username already taken'
    assert created_user.status_code == 200
    data = created_user.json()
    assert isinstance(data, dict)
    assert data.get('username') == 'Luna'


@pytest.mark.asyncio
async def test_login_user(client, created_user):
    response = await client.post('/api/v1/users/login', data={'username': 'Luna', 'password': 'vulpkanin'})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "access_token" in data
    assert data.get("token_type") == 'bearer'
    

@pytest.mark.asyncio
async def test_delete_user(client, created_user, admin_token, user_token):
    data = created_user.json()
    assert created_user.status_code == 200
    assert isinstance(data, dict)
    assert data.get('username') == 'Luna'
    response = await client.request('DELETE', '/api/v1/users/', json={'username': 'Luna'}, headers=user_token)
    assert response.status_code == 403
    response = await client.request('DELETE', '/api/v1/users/', json={'username': 'Luna'}, headers=admin_token)
    assert response.status_code == 200