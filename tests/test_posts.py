import pytest

@pytest.mark.asyncio
async def test_create_post(client):
    test_text = 'Noice little text'
    response = await client.post('/api/v1/posts/', json={'text': test_text})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert data.get('text') == test_text
    assert 'created_at' in data

@pytest.mark.asyncio
async def test_show_latest_posts(client):
    response = await client.get('/api/v1/posts/')
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert 'text' in data

@pytest.mark.asyncio
async def test_read_todays_post(client):
    response = await client.get('/api/v1/posts/today')
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert 'text' in data

@pytest.mark.asyncio
async def test_delete_post(client):
    response = await client.delete('/api/v1/posts/335')
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert data.get('deleted') == '335'
    assert 'text' in data