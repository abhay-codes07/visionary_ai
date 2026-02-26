from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

DetectionLabel = str
EventType = Literal["detection", "reasoning", "token", "session", "error"]


class BoundingBox(BaseModel):
    x: float = Field(ge=0)
    y: float = Field(ge=0)
    width: float = Field(ge=0)
    height: float = Field(ge=0)


class LiveDetection(BaseModel):
    label: DetectionLabel
    confidence: float = Field(ge=0, le=1)
    box: BoundingBox


class LiveFramePayload(BaseModel):
    session_id: str
    frame_id: str
    mime_type: Literal["image/jpeg", "image/png"] = "image/jpeg"
    image_base64: str
    question: str | None = None
    demo_mode: Literal["security", "workspace", "objects", "custom"] = "custom"


class LiveFrameAnalysis(BaseModel):
    session_id: str
    frame_id: str
    detections: list[LiveDetection]
    summary: str
    processed_at: datetime


class LiveStreamEvent(BaseModel):
    type: EventType
    session_id: str
    frame_id: str | None = None
    content: str
    detections: list[LiveDetection] = []
    timestamp: datetime
