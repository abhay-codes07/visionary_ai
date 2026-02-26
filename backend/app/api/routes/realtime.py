import asyncio
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import ValidationError

from app.core.errors import VisionaryError
from app.schemas.realtime import RealtimeInboundMessage, RealtimeOutboundMessage
from app.schemas.vision import VisionAnalyzeRequest, VisionQuestionRequest
from app.services.realtime_manager import RealtimeConnectionManager
from app.services.streaming_service import StreamingService
from app.services.vision_service import VisionService

router = APIRouter()
manager = RealtimeConnectionManager()
vision_service = VisionService()
streaming_service = StreamingService()


@router.websocket("/ws")
async def realtime_gateway(websocket: WebSocket) -> None:
    await manager.connect(websocket)
    await manager.send_message(
        websocket,
        RealtimeOutboundMessage(type="connected", content="Realtime session established.", timestamp=datetime.now(timezone.utc)),
    )
    try:
        while True:
            raw_message = await websocket.receive_json()
            try:
                inbound = RealtimeInboundMessage.model_validate(raw_message)
                await _dispatch_inbound(websocket, inbound)
            except ValidationError as exc:
                await _send_error(websocket, f"Invalid realtime payload: {exc.errors()[0]['msg']}", None)
            except VisionaryError as exc:
                await _send_error(websocket, exc.message, inbound.request_id if "inbound" in locals() else None)
            except Exception:
                await _send_error(websocket, "Unexpected realtime processing error.", None)
    except WebSocketDisconnect:
        manager.disconnect(websocket)


async def _dispatch_inbound(websocket: WebSocket, message: RealtimeInboundMessage) -> None:
    if message.type == "ping":
        await manager.send_message(
            websocket,
            RealtimeOutboundMessage(type="token", content="pong", request_id=message.request_id, timestamp=datetime.now(timezone.utc)),
        )
        return

    if message.type == "analyze":
        analyze_response = await vision_service.analyze(
            VisionAnalyzeRequest(
                media_type=message.media_type or "image",
                prompt=message.prompt or "Describe this scene.",
            )
        )
        await manager.send_message(
            websocket,
            RealtimeOutboundMessage(
                type="analysis",
                request_id=analyze_response.request_id,
                content=analyze_response.summary,
                timestamp=datetime.now(timezone.utc),
            ),
        )
        token_events = await streaming_service.stream_analysis(analyze_response.request_id, analyze_response.summary)
        for event in token_events:
            await manager.send_message(websocket, event)
            await asyncio.sleep(0.04)
        await manager.send_message(
            websocket,
            RealtimeOutboundMessage(
                type="completed",
                request_id=analyze_response.request_id,
                content="Analysis complete.",
                timestamp=datetime.now(timezone.utc),
            ),
        )
        return

    question_payload = VisionQuestionRequest(
        request_id=message.request_id or str(uuid4()),
        question=message.question or "What is happening in this scene?",
    )
    question_response = await vision_service.answer_question(question_payload)
    token_events = await streaming_service.stream_answer(question_response.request_id, question_response.answer)
    for event in token_events:
        await manager.send_message(websocket, event)
        await asyncio.sleep(0.04)
    await manager.send_message(
        websocket,
        RealtimeOutboundMessage(
            type="completed",
            request_id=question_response.request_id,
            content="Question processing complete.",
            timestamp=datetime.now(timezone.utc),
        ),
    )


async def _send_error(websocket: WebSocket, message: str, request_id: str | None) -> None:
    await manager.send_message(
        websocket,
        RealtimeOutboundMessage(
            type="error",
            request_id=request_id,
            content=message,
            timestamp=datetime.now(timezone.utc),
        ),
    )

