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
