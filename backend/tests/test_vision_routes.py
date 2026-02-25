from fastapi.testclient import TestClient

from app.main import app


def test_analyze_route_returns_summary_and_detections() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/v1/vision/analyze",
        json={"media_type": "image", "prompt": "Describe the workspace scene"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["media_type"] == "image"
    assert isinstance(payload["summary"], str) and payload["summary"]
    assert isinstance(payload["detections"], list) and payload["detections"]


def test_capabilities_route_returns_supported_contract() -> None:
    client = TestClient(app)

    response = client.get("/api/v1/vision/capabilities")

    assert response.status_code == 200
    payload = response.json()
    assert payload["supports_streaming"] is True
    assert "image" in payload["supported_media_types"]
    assert "websocket" in payload["supported_transports"]
    assert isinstance(payload["model"], str) and payload["model"]
    assert isinstance(payload["openai_enabled"], bool)
    assert isinstance(payload["fallback_mode"], bool)


def test_question_route_rejects_blank_question() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/v1/vision/question",
        json={"request_id": "req-1", "question": "   "},
    )

    assert response.status_code == 422
    payload = response.json()
    assert payload["error"]["code"] == "invalid_input"


def test_upload_route_returns_storage_metadata() -> None:
    client = TestClient(app)

    files = {"file": ("frame.jpg", b"fake-image-bytes", "image/jpeg")}
    data = {"media_type": "image"}
    response = client.post("/api/v1/vision/upload", data=data, files=files)

    assert response.status_code == 200
    payload = response.json()
    assert payload["filename"] == "frame.jpg"
    assert payload["media_type"] == "image"
    assert payload["size_bytes"] == len(b"fake-image-bytes")


def test_stream_analyze_route_returns_sse_chunks() -> None:
    client = TestClient(app)

    with client.stream(
        "POST",
        "/api/v1/vision/analyze/stream",
        json={"media_type": "image", "prompt": "Stream scene reasoning"},
    ) as response:
        assert response.status_code == 200
        body = "".join(response.iter_text())

    assert "data: " in body
    assert '"token"' in body
    assert "[DONE]" in body


def test_stream_question_route_returns_sse_chunks() -> None:
    client = TestClient(app)

    with client.stream(
        "POST",
        "/api/v1/vision/question/stream",
        json={"request_id": "stream-q-1", "question": "What is visible in this scene?"},
    ) as response:
        assert response.status_code == 200
        body = "".join(response.iter_text())

    assert "data: " in body
    assert '"request_id":"stream-q-1"' in body
    assert "[DONE]" in body
