from datetime import UTC, datetime
from uuid import uuid4

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.schemas.realtime import RealtimeInboundMessage, RealtimeOutboundMessage
from app.schemas.vision import VisionAnalyzeRequest, VisionQuestionRequest
from app.services.realtime_manager import RealtimeConnectionManager
from app.services.vision_service import VisionService

router = APIRouter()
manager = RealtimeConnectionManager()
vision_service = VisionService()


@router.websocket("/ws")
async def realtime_gateway(websocket: WebSocket) -> None:
    await manager.connect(websocket)
    await manager.send_message(
        websocket,
        RealtimeOutboundMessage(type="connected", content="Realtime session established.", timestamp=datetime.now(UTC)),
    )
    try:
        while True:
            raw_message = await websocket.receive_json()
            inbound = RealtimeInboundMessage.model_validate(raw_message)
            await _dispatch_inbound(websocket, inbound)
    except WebSocketDisconnect:
        manager.disconnect(websocket)


async def _dispatch_inbound(websocket: WebSocket, message: RealtimeInboundMessage) -> None:
    if message.type == "ping":
        await manager.send_message(
            websocket,
            RealtimeOutboundMessage(type="token", content="pong", request_id=message.request_id, timestamp=datetime.now(UTC)),
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
                timestamp=datetime.now(UTC),
            ),
        )
        await manager.send_message(
            websocket,
            RealtimeOutboundMessage(
                type="completed",
                request_id=analyze_response.request_id,
                content="Analysis complete.",
                timestamp=datetime.now(UTC),
            ),
        )
        return

    question_payload = VisionQuestionRequest(
        request_id=message.request_id or str(uuid4()),
        question=message.question or "What is happening in this scene?",
    )
    question_response = await vision_service.answer_question(question_payload)
    await manager.send_message(
        websocket,
        RealtimeOutboundMessage(
            type="token",
            request_id=question_response.request_id,
            content=question_response.answer,
            timestamp=datetime.now(UTC),
        ),
    )
