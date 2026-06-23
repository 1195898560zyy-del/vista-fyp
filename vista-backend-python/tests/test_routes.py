import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_health(client):
    r = await client.get("/")
    assert r.status_code == 200
    assert r.text == "VISTA backend is running."


@pytest.mark.asyncio
async def test_session_flow(client):
    r = await client.post("/api/session")
    assert r.status_code == 200
    data = r.json()
    assert "session" in data
    assert data["code"].startswith("VISTA-")

    session_id = data["session"]
    r = await client.get(f"/api/session/{session_id}")
    assert r.status_code == 200
    assert r.json() == {"ok": True}

    r = await client.post(
        "/api/cmd",
        json={"session": session_id, "command": {"type": "test", "value": 1}},
    )
    assert r.status_code == 200
    cmd_id = r.json()["id"]

    r = await client.get(f"/api/check?session={session_id}")
    assert r.status_code == 200
    cmd = r.json()["command"]
    assert cmd is not None
    assert cmd["id"] == cmd_id
    assert cmd["status"] == "executed"

    r = await client.get(f"/api/status?session={session_id}&id={cmd_id}")
    assert r.status_code == 200
    assert r.json()["status"] == "executed"


@pytest.mark.asyncio
async def test_weather_missing_lat(client):
    r = await client.get("/api/weather")
    assert r.status_code == 400
    assert r.json()["error"] == "Missing or invalid lat/lon"


@pytest.mark.asyncio
async def test_unsplash_missing_query(client):
    r = await client.get("/api/unsplash")
    assert r.status_code == 400
    assert r.json()["error"] == "Missing ?q="


@pytest.mark.asyncio
async def test_agent_missing_message(client):
    r = await client.post("/api/agent", json={})
    assert r.status_code == 422
