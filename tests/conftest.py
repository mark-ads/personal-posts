from collections.abc import AsyncGenerator
import pytest
from httpx import AsyncClient, ASGITransport
import pytest_asyncio
from src.main import app

@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac