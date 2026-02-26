from __future__ import annotations

from datetime import UTC, datetime

from app.schemas.live import LiveDetection, LiveFrameAnalysis, LiveFramePayload
from app.services.vision_agent_service import VisionAgentService
from app.services.yolo_service import YoloService


class LiveSessionState:
    def __init__(self) -> None:
        self.latest_detections: list[LiveDetection] = []
        self.latest_reasoning: str = ""
        self.updated_at: datetime = datetime.now(UTC)


class LiveStreamService:
    def __init__(self) -> None:
        self._yolo = YoloService()
        self._agent = VisionAgentService()
        self._sessions: dict[str, LiveSessionState] = {}

    async def analyze_frame(self, payload: LiveFramePayload) -> LiveFrameAnalysis:
        detections = self._yolo.detect_from_base64(payload.image_base64)
        reasoning = await self._agent.reason(
            prompt=payload.question or "Describe current scene state.",
            detections=detections,
            demo_mode=payload.demo_mode,
        )
        state = self._sessions.setdefault(payload.session_id, LiveSessionState())
        state.latest_detections = detections
        state.latest_reasoning = reasoning
        state.updated_at = datetime.now(UTC)
        return LiveFrameAnalysis(
            session_id=payload.session_id,
            frame_id=payload.frame_id,
            detections=detections,
            summary=reasoning,
            processed_at=datetime.now(UTC),
        )

    async def answer_live_question(self, session_id: str, question: str, demo_mode: str = "custom") -> str:
        state = self._sessions.setdefault(session_id, LiveSessionState())
        answer = await self._agent.answer_question(question, state.latest_detections, demo_mode=demo_mode)
        state.latest_reasoning = answer
        state.updated_at = datetime.now(UTC)
        return answer

    def get_session_snapshot(self, session_id: str) -> LiveSessionState:
        return self._sessions.setdefault(session_id, LiveSessionState())
