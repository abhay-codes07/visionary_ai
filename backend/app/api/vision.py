from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.api.deps import get_live_stream_service
from app.services.live_stream_service import LiveStreamService

router = APIRouter(prefix="/live")


class LiveQuestionRequest(BaseModel):
    session_id: str
    question: str
    demo_mode: str = "custom"


class LiveQuestionResponse(BaseModel):
    session_id: str
    answer: str
    generated_at: datetime


class LiveSessionSnapshotResponse(BaseModel):
    session_id: str
    detection_count: int
    reasoning: str
    updated_at: datetime


@router.get("/sessions/{session_id}", response_model=LiveSessionSnapshotResponse)
async def get_live_session_snapshot(
    session_id: str, live_service: LiveStreamService = Depends(get_live_stream_service)
) -> LiveSessionSnapshotResponse:
    snapshot = live_service.get_session_snapshot(session_id)
    return LiveSessionSnapshotResponse(
        session_id=session_id,
        detection_count=len(snapshot.latest_detections),
        reasoning=snapshot.latest_reasoning,
        updated_at=snapshot.updated_at,
    )


@router.post("/question", response_model=LiveQuestionResponse)
async def answer_live_question(
    payload: LiveQuestionRequest, live_service: LiveStreamService = Depends(get_live_stream_service)
) -> LiveQuestionResponse:
    answer = await live_service.answer_live_question(
        session_id=payload.session_id,
        question=payload.question,
        demo_mode=payload.demo_mode,
    )
    return LiveQuestionResponse(
        session_id=payload.session_id,
        answer=answer,
        generated_at=datetime.now(UTC),
    )
