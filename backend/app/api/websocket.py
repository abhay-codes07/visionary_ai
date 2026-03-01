from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import ValidationError

from app.api.deps import get_cognitive_pipeline, get_live_stream_service, get_stream_service
from app.schemas.live import LiveDetection, LiveFramePayload, LiveStreamEvent
from app.services.cognitive_pipeline import CognitivePipeline
from app.services.live_stream_service import LiveStreamService
from app.services.stream_service import StreamService

logger = logging.getLogger(__name__)

router = APIRouter()
live_service = get_live_stream_service()
stream_service = get_stream_service()
cognitive = get_cognitive_pipeline()


@router.websocket("/ws/live")
async def live_vision_gateway(websocket: WebSocket) -> None:
    await websocket.accept()
    logger.info("[ws/live] client connected")
    await websocket.send_json(
        LiveStreamEvent(
            type="session",
            session_id="bootstrap",
            content="Live cognitive vision gateway connected.",
            timestamp=datetime.now(timezone.utc),
        ).model_dump(mode="json")
    )
    try:
        while True:
            incoming = await websocket.receive_json()
            message_type = incoming.get("type")

            if message_type == "frame":
                await _handle_cognitive_frame(websocket, incoming)
            elif message_type == "question":
                await _handle_question(websocket, incoming)
            else:
                await _send_error(websocket, "Unsupported live message type.", incoming.get("session_id") or "unknown")
    except WebSocketDisconnect:
        logger.info("[ws/live] client disconnected")
        return


async def _handle_cognitive_frame(websocket: WebSocket, incoming: dict) -> None:
    """Process a frame through the full cognitive pipeline."""
    sid = "unknown"
    try:
        payload = LiveFramePayload.model_validate(incoming["payload"])
        sid = payload.session_id
    except (KeyError, ValidationError) as exc:
        logger.warning("[ws/live] invalid frame payload: %s", exc)
        await _send_error(websocket, "Invalid frame payload.", incoming.get("session_id") or "unknown")
        return

    try:
        events = await cognitive.process_frame(payload)
    except Exception as exc:
        logger.exception("[ws/live] cognitive pipeline error: %s", exc)
        await _send_error(websocket, f"Frame analysis error: {exc}", sid)
        return

    # Emit cognitive events over the WebSocket
    for ev in events:
        etype = ev.event_type.lower()
        if etype == "detection":
            # Build LiveDetection objects from raw dicts for the event
            raw_dets = ev.payload.get("detections", [])
            det_objects = []
            for rd in raw_dets:
                try:
                    det_objects.append(LiveDetection.model_validate(rd))
                except Exception:
                    pass
            await websocket.send_json(
                LiveStreamEvent(
                    type="detection",
                    session_id=sid,
                    frame_id=ev.payload.get("frame_id"),
                    content=f"{ev.payload.get('count', 0)} objects detected.",
                    detections=det_objects,
                    timestamp=datetime.now(timezone.utc),
                    data={"labels": ev.payload.get("labels", [])},
                ).model_dump(mode="json")
            )
        elif etype == "state_change":
            await websocket.send_json(
                LiveStreamEvent(
                    type="state_change",
                    session_id=sid,
                    content=f"State changed: {ev.payload.get('previous_state')} → {ev.payload.get('new_state')}",
                    timestamp=datetime.now(timezone.utc),
                    data=ev.payload,
                ).model_dump(mode="json")
            )
        elif etype == "alert":
            await websocket.send_json(
                LiveStreamEvent(
                    type="alert",
                    session_id=sid,
                    content=ev.payload.get("message", "Alert"),
                    timestamp=datetime.now(timezone.utc),
                    data=ev.payload,
                ).model_dump(mode="json")
            )
        elif etype == "summary":
            await websocket.send_json(
                LiveStreamEvent(
                    type="summary",
                    session_id=sid,
                    content=ev.payload.get("text", ""),
                    timestamp=datetime.now(timezone.utc),
                    data=ev.payload,
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
            timestamp=datetime.now(timezone.utc),
        ).model_dump(mode="json")
    )

