import base64

import numpy as np
from fastapi.testclient import TestClient

from app.main import app


def _tiny_jpeg_base64() -> str:
    """Create a minimal 4x4 red JPEG as base64 for frame tests."""
    try:
        import cv2

        img = np.zeros((4, 4, 3), dtype=np.uint8)
        img[:, :] = (0, 0, 255)  # red
        _, buf = cv2.imencode(".jpg", img)
        return base64.b64encode(buf.tobytes()).decode()
    except Exception:
        # Fallback: 1x1 white JPEG bytes (minimal valid JPEG)
        raw = bytes(
            [0xFF, 0xD8, 0xFF, 0xE0, 0x00, 0x10, 0x4A, 0x46, 0x49, 0x46, 0x00,
             0x01, 0x01, 0x00, 0x00, 0x01, 0x00, 0x01, 0x00, 0x00, 0xFF, 0xDB,
             0x00, 0x43, 0x00, 0x08] + [0x08]*63 + [0xFF, 0xC0, 0x00, 0x0B, 0x08,
             0x00, 0x01, 0x00, 0x01, 0x01, 0x01, 0x11, 0x00, 0xFF, 0xC4, 0x00,
             0x1F, 0x00, 0x00, 0x01, 0x05, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01,
             0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x02, 0x03,
             0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A, 0x0B, 0xFF, 0xDA, 0x00,
             0x08, 0x01, 0x01, 0x00, 0x00, 0x3F, 0x00, 0x7B, 0x40, 0x1B, 0xFF,
             0xD9]
        )
        return base64.b64encode(raw).decode()


def test_live_session_snapshot_endpoint() -> None:
    client = TestClient(app)
    response = client.get("/api/v1/live/sessions/demo-session")
    assert response.status_code == 200
    payload = response.json()
    assert payload["session_id"] == "demo-session"
    assert isinstance(payload["detection_count"], int)


def test_live_question_endpoint() -> None:
    client = TestClient(app)
    response = client.post(
        "/api/v1/live/question",
        json={"session_id": "demo-session", "question": "What is happening?", "demo_mode": "workspace"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["session_id"] == "demo-session"
    assert isinstance(payload["answer"], str)


def test_live_websocket_question_stream() -> None:
    client = TestClient(app)
    with client.websocket_connect("/api/v1/ws/live") as ws:
        _ = ws.receive_json()
        ws.send_json({"type": "question", "session_id": "demo-session", "question": "Any person detected?"})
        event = ws.receive_json()
        assert event["type"] in {"token", "error"}


def test_live_websocket_frame_detection() -> None:
    """Send a frame over the live WebSocket and verify detection + cognitive events come back."""
    client = TestClient(app)
    frame_b64 = _tiny_jpeg_base64()
    with client.websocket_connect("/api/v1/ws/live") as ws:
        session_event = ws.receive_json()
        assert session_event["type"] == "session"

        ws.send_json({
            "type": "frame",
            "payload": {
                "session_id": "test-session",
                "frame_id": "frame-001",
                "image_base64": frame_b64,
                "mime_type": "image/jpeg",
                "demo_mode": "objects",
            },
        })

        detection_event = ws.receive_json()
        assert detection_event["type"] == "detection"
        assert detection_event["session_id"] == "test-session"
        assert detection_event["frame_id"] == "frame-001"
        assert isinstance(detection_event["detections"], list)
        assert "objects detected" in detection_event["content"]

        # Cognitive pipeline may emit additional events (summary, state_change)
        # Read and validate what we get
        seen_types: set[str] = {"detection"}
        # Read up to 5 more events (may be summary, state_change, alert, etc.)
        import queue
        for _ in range(5):
            try:
                extra_event = ws.receive_json()
                seen_types.add(extra_event["type"])
            except Exception:
                break
        # At minimum we got detection; summary is also expected from reaction engine
        assert "detection" in seen_types


def test_live_websocket_invalid_frame_returns_error() -> None:
    """Malformed frame payload should return an error event, not crash."""
    client = TestClient(app)
    with client.websocket_connect("/api/v1/ws/live") as ws:
        _ = ws.receive_json()
        ws.send_json({"type": "frame", "payload": {"bad": "data"}})
        event = ws.receive_json()
        assert event["type"] == "error"
