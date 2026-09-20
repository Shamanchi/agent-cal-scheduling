"""API-тесты без сети: TestClient."""

import pytest
from fastapi.testclient import TestClient

from app.main import create_app

PAYLOAD = {
    "day": "2026-09-22",
    "duration_min": 30,
    "attendees": [
        {"name": "Ann", "busy": [{"start": "2026-09-22T10:00", "end": "2026-09-22T11:00"}]},
        {"name": "Bob", "busy": [{"start": "2026-09-22T10:30", "end": "2026-09-22T12:00"}]},
    ],
}


@pytest.fixture()
def client() -> TestClient:
    return TestClient(create_app())


def test_health(client: TestClient) -> None:
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_slots(client: TestClient) -> None:
    resp = client.post("/api/v1/slots", json=PAYLOAD)
    assert resp.status_code == 200
    slots = resp.json()["slots"]
    assert slots[0] == {"start": "2026-09-22T09:00", "end": "2026-09-22T10:00"}
    assert slots[-1]["end"] == "2026-09-22T18:00"


def test_slots_rejects_bad_day(client: TestClient) -> None:
    bad = dict(PAYLOAD, day="tomorrow")
    resp = client.post("/api/v1/slots", json=bad)
    assert resp.status_code == 422


@pytest.mark.integration()
def test_custom_hours_shape(client: TestClient) -> None:
    """Интеграционный по маркеру: свои рабочие часы, без сети."""
    payload = dict(PAYLOAD, work_start="10:00", work_end="13:00")
    resp = client.post("/api/v1/slots", json=payload)
    assert resp.status_code == 200
    assert resp.json()["slots"] == [{"start": "2026-09-22T12:00", "end": "2026-09-22T13:00"}]
