from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.api.deps import get_cognitive_pipeline, get_live_stream_service
from app.services.cognitive_pipeline import CognitivePipeline
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
    # Cognitive extensions
    state: Optional[str] = None
    state_duration: Optional[float] = None
    confidence: Optional[float] = None
    behaviors: Optional[List[Dict[str, Any]]] = None
    transitions: Optional[List[Dict[str, Any]]] = None
    mode: Optional[str] = None


@router.get("/sessions/{session_id}", response_model=LiveSessionSnapshotResponse)
async def get_live_session_snapshot(
    session_id: str,
    live_service: LiveStreamService = Depends(get_live_stream_service),
    pipeline: CognitivePipeline = Depends(get_cognitive_pipeline),
) -> LiveSessionSnapshotResponse:
    snapshot = live_service.get_session_snapshot(session_id)
    cog = pipeline.get_session_snapshot(session_id)
    return LiveSessionSnapshotResponse(
        session_id=session_id,
        detection_count=cog.get("detection_count", len(snapshot.latest_detections)),
        reasoning=cog.get("reason", snapshot.latest_reasoning),
        updated_at=snapshot.updated_at,
        state=cog.get("state"),
        state_duration=cog.get("state_since"),
        confidence=cog.get("confidence"),
        behaviors=cog.get("behaviors"),
        transitions=cog.get("transitions"),
        mode=cog.get("mode"),
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
        generated_at=datetime.now(timezone.utc),
    )

