from fastapi.testclient import TestClient

from app.main import app


def test_websocket_connect_and_ping_flow() -> None:
    client = TestClient(app)
    with client.websocket_connect("/api/v1/ws") as websocket:
        connected = websocket.receive_json()
        assert connected["type"] == "connected"

        websocket.send_json({"type": "ping", "request_id": "req-ping"})
        pong = websocket.receive_json()
        assert pong["type"] == "token"
        assert pong["request_id"] == "req-ping"
        assert pong["content"] == "pong"


def test_websocket_analyze_flow_emits_analysis_and_completed() -> None:
    client = TestClient(app)
    with client.websocket_connect("/api/v1/ws") as websocket:
        _ = websocket.receive_json()
        websocket.send_json({"type": "analyze", "media_type": "image", "prompt": "Analyze the scene"})

        analysis = websocket.receive_json()
        assert analysis["type"] == "analysis"
        assert isinstance(analysis["request_id"], str) and analysis["request_id"]
        assert isinstance(analysis["content"], str) and analysis["content"]

        completed = websocket.receive_json()
        assert completed["type"] == "completed"
        assert completed["request_id"] == analysis["request_id"]


def test_websocket_question_flow_emits_token_answer() -> None:
    client = TestClient(app)
    with client.websocket_connect("/api/v1/ws") as websocket:
        _ = websocket.receive_json()
        websocket.send_json(
            {"type": "question", "request_id": "req-question", "question": "What objects are visible?"}
        )

        answer = websocket.receive_json()
        assert answer["type"] == "token"
        assert answer["request_id"] == "req-question"
        assert isinstance(answer["content"], str) and "req-question" in answer["content"]
