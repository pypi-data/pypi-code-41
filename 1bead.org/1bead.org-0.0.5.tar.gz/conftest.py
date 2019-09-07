import pytest

from web.core import app


@pytest.fixture
async def client(aiohttp_client):
    return await aiohttp_client(app)
