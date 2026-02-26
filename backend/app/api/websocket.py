from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from uuid import uuid4

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import ValidationError

from app.api.deps import get_live_stream_service, get_stream_service
from app.schemas.live import LiveFramePayload, LiveStreamEvent
from app.services.live_stream_service import LiveStreamService
from app.services.stream_service import StreamService

router = APIRouter()
live_service = get_live_stream_service()
stream_service = get_stream_service()


@router.websocket("/ws/live")
async def live_vision_gateway(websocket: WebSocket) -> None:
    await websocket.accept()
    await websocket.send_json(
        LiveStreamEvent(
            type="session",
            session_id="bootstrap",
            content="Live vision gateway connected.",
            timestamp=datetime.now(UTC),
        ).model_dump(mode="json")
    )
    try:
        while True:
            incoming = await websocket.receive_json()
            message_type = incoming.get("type")

            if message_type == "frame":
                await _handle_frame(websocket, incoming)
            elif message_type == "question":
                await _handle_question(websocket, incoming)
            else:
                await _send_error(websocket, "Unsupported live message type.", incoming.get("session_id") or "unknown")
    except WebSocketDisconnect:
        return


async def _handle_frame(websocket: WebSocket, incoming: dict) -> None:
    try:
        payload = LiveFramePayload.model_validate(incoming["payload"])
    except (KeyError, ValidationError):
        await _send_error(websocket, "Invalid frame payload.", incoming.get("session_id") or "unknown")
        return

    analysis = await live_service.analyze_frame(payload)
    await websocket.send_json(
        LiveStreamEvent(
            type="detection",
            session_id=analysis.session_id,
            frame_id=analysis.frame_id,
            content=f"{len(analysis.detections)} objects detected.",
            detections=analysis.detections,
            timestamp=datetime.now(UTC),
        ).model_dump(mode="json")
    )
    await websocket.send_json(
        LiveStreamEvent(
            type="reasoning",
            session_id=analysis.session_id,
            frame_id=analysis.frame_id,
            content=analysis.summary,
            detections=analysis.detections,
            timestamp=datetime.now(UTC),
        ).model_dump(mode="json")
    )


async def _handle_question(websocket: WebSocket, incoming: dict) -> None:
    session_id = incoming.get("session_id") or "unknown"
    question = incoming.get("question") or ""
    demo_mode = incoming.get("demo_mode") or "custom"
    if not question.strip():
        await _send_error(websocket, "Question cannot be empty.", session_id)
        return

    answer = await live_service.answer_live_question(session_id=session_id, question=question, demo_mode=demo_mode)
    token_events = await stream_service.tokenize(text=answer, session_id=session_id, frame_id=str(uuid4()))
    for event in token_events:
        await websocket.send_json(event.model_dump(mode="json"))
        await asyncio.sleep(0.035)


async def _send_error(websocket: WebSocket, message: str, session_id: str) -> None:
    await websocket.send_json(
        LiveStreamEvent(
            type="error",
            session_id=session_id,
            content=message,
            timestamp=datetime.now(UTC),
        ).model_dump(mode="json")
    )
