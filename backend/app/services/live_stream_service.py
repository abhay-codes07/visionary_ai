from __future__ import annotations

import asyncio
from datetime import datetime, timezone

from app.core.config import get_settings
from app.schemas.live import LiveDetection, LiveFrameAnalysis, LiveFramePayload
from app.services.vision_agent_service import VisionAgentService
from app.services.yolo_service import YoloService


class LiveSessionState:
    def __init__(self) -> None:
        self.latest_detections: list[LiveDetection] = []
        self.latest_reasoning: str = ""
        self.updated_at: datetime = datetime.now(timezone.utc)


class LiveStreamService:
    def __init__(self) -> None:
        settings = get_settings()
        self._yolo = YoloService()
        self._agent = VisionAgentService()
        self._sessions: dict[str, LiveSessionState] = {}
        self._queues: dict[str, asyncio.Queue[tuple[LiveFramePayload, asyncio.Future[LiveFrameAnalysis]]]] = {}
        self._workers: dict[str, asyncio.Task] = {}
        self._queue_size = max(1, settings.live_frame_queue_size)

    async def analyze_frame(self, payload: LiveFramePayload) -> LiveFrameAnalysis:
        queue = self._queues.setdefault(payload.session_id, asyncio.Queue(maxsize=self._queue_size))
        if payload.session_id not in self._workers:
            self._workers[payload.session_id] = asyncio.create_task(self._worker(payload.session_id))

        if queue.full():
            try:
                queue.get_nowait()
                queue.task_done()
            except asyncio.QueueEmpty:
                pass

        loop = asyncio.get_running_loop()
        future: asyncio.Future[LiveFrameAnalysis] = loop.create_future()
        await queue.put((payload, future))
        return await future

    async def _worker(self, session_id: str) -> None:
        queue = self._queues[session_id]
        while True:
            payload, future = await queue.get()
            try:
                result = await self._analyze_now(payload)
                if not future.cancelled():
                    future.set_result(result)
            except Exception as exc:  # pragma: no cover
                if not future.cancelled():
                    future.set_exception(exc)
            finally:
                queue.task_done()

    async def _analyze_now(self, payload: LiveFramePayload) -> LiveFrameAnalysis:
        detections = self._yolo.detect_from_base64(payload.image_base64)
        reasoning = await self._agent.reason(
            prompt=payload.question or "Describe current scene state.",
            detections=detections,
            demo_mode=payload.demo_mode,
        )
        state = self._sessions.setdefault(payload.session_id, LiveSessionState())
        state.latest_detections = detections
        state.latest_reasoning = reasoning
        state.updated_at = datetime.now(timezone.utc)
        return LiveFrameAnalysis(
            session_id=payload.session_id,
            frame_id=payload.frame_id,
            detections=detections,
            summary=reasoning,
            processed_at=datetime.now(timezone.utc),
        )

    async def answer_live_question(self, session_id: str, question: str, demo_mode: str = "custom") -> str:
        state = self._sessions.setdefault(session_id, LiveSessionState())
        answer = await self._agent.answer_question(question, state.latest_detections, demo_mode=demo_mode)
        state.latest_reasoning = answer
        state.updated_at = datetime.now(timezone.utc)
        return answer

    def get_session_snapshot(self, session_id: str) -> LiveSessionState:
        return self._sessions.setdefault(session_id, LiveSessionState())

