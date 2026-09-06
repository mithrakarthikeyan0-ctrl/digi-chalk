import pytest
from httpx import AsyncClient
from app.main import app
from app.storage.database import init_db

@pytest.fixture(autouse=True)
async def setup_db():
    await init_db()

@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/health/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@pytest.mark.asyncio
async def test_session_lifecycle():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        start_res = await ac.post("/sessions/", json={"classroom": "123", "status": "recording"})
        assert start_res.status_code == 200
        session_id = start_res.json()["id"]

        end_res = await ac.post(f"/sessions/{session_id}/end/")
        assert end_res.status_code == 200
        assert end_res.json()["status"] == "ended"

@pytest.mark.asyncio
async def test_stroke_simulation():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        start_res = await ac.post("/sessions/", json={"classroom": "123", "status": "recording"})
        session_id = start_res.json()["id"]

        stroke_payload = {
            "type": "stroke",
            "sessionId": session_id,
            "strokeId": "s1",
            "points": [{"x": 10, "y": 20, "dt": 1, "color": "#FFF"}]
        }
        res = await ac.post("/simulate/stroke/", json=stroke_payload)
        assert res.status_code == 200

        events_res = await ac.get(f"/sessions/{session_id}/events/")
        events = events_res.json()["events"]
        assert len(events) == 1
        assert events[0]["strokeId"] == "s1"
