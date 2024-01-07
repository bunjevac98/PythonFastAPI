import httpx
import pytest
import asyncio
from app.main import app

@pytest.mark.asyncio
async def test_root():
    async with httpx.AsyncClient(app=app, base_url="http://test") as client:
        response= await client.get("/")
    assert response.status_code ==200
    assert response.json() == {"message": "Welcome to API"}