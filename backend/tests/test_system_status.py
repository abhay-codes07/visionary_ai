from fastapi.testclient import TestClient

from app.main import app


def test_system_status_endpoint_returns_runtime_flags() -> None:
    client = TestClient(app)

    response = client.get("/api/v1/system/status")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert isinstance(payload["uptime_seconds"], int)
    assert isinstance(payload["openai_enabled"], bool)
    assert isinstance(payload["fallback_mode"], bool)
