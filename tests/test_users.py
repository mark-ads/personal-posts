import pytest

@pytest.mark.asyncio
async def test_create_user(client):
    response = await client.post('/api/v1/users/', json={'username': 'Luna'})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert data.get('username') == 'Luna'
    assert "authorized" in data

@pytest.mark.asyncio
async def test_login_user(client):
    response = await client.post('/api/v1/users/login', data={'username': 'Luna', 'password': 'Noice'})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert data.get('username') == 'Luna'
    assert "authorized" in data
    
@pytest.mark.asyncio
async def test_delete_user(client):
    response = await client.request('DELETE', '/api/v1/users/', json={'username': 'Luna'})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert data.get('username') == 'Luna'
    assert "authorized" in data