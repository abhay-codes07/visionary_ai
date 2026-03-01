"""Cognitive Pipeline – orchestrates the full vision cognition loop.

    Camera Frame → YOLO → Temporal Memory → Behavior Engine
                              → State Engine → Reaction Engine → Events

This service replaces the old per-frame reasoning approach with a *temporal,
stateful* pipeline that understands behavior over time.
"""

from __future__ import annotations

import asyncio
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from typing import Dict, List, Optional

from app.core.config import get_settings
from app.schemas.live import LiveDetection, LiveFramePayload
from app.services.behavior_engine import BehaviorResult, infer_behaviors
from app.services.reaction_engine import CognitiveEvent, ReactionEngine
from app.services.state_engine import BrainState, StateEngine
from app.services.temporal_memory import TemporalMemory
from app.services.yolo_service import YoloService

logger = logging.getLogger(__name__)

_yolo_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="yolo")


class CognitiveSession:
    """Full cognitive state for a single WebSocket session."""

    def __init__(self, session_id: str) -> None:
        self.session_id = session_id
        self.memory = TemporalMemory()
        self.state_engine = StateEngine()
        self.reaction_engine = ReactionEngine()
        self.latest_detections: List[LiveDetection] = []
        self.latest_behaviors: List[BehaviorResult] = []
        self.demo_mode: str = "workspace"
        self._last_behavior_tick: float = 0.0


class CognitivePipeline:
    """Singleton pipeline — one per application."""

    def __init__(self) -> None:
        self._yolo = YoloService()
        self._sessions: Dict[str, CognitiveSession] = {}
        self._queues: Dict[str, asyncio.Queue] = {}
        self._workers: Dict[str, asyncio.Task] = {}
        settings = get_settings()
        self._queue_size = max(1, settings.live_frame_queue_size)

    # ------------------------------------------------------------------
    # Public API – called from the WebSocket handler
    # ------------------------------------------------------------------
    async def process_frame(self, payload: LiveFramePayload) -> List[CognitiveEvent]:
        """Accept a frame, run YOLO, feed into cognitive engines.

        Returns a list of CognitiveEvents to send over the WebSocket.
        """
        session = self._sessions.setdefault(
            payload.session_id,
            CognitiveSession(payload.session_id),
        )
        session.demo_mode = payload.demo_mode or "workspace"

        queue = self._queues.setdefault(
            payload.session_id,
            asyncio.Queue(maxsize=self._queue_size),
        )
        if payload.session_id not in self._workers:
            self._workers[payload.session_id] = asyncio.create_task(
                self._worker(payload.session_id)
            )

        # Drop stale frames
        if queue.full():
            try:
                _old_payload, old_future = queue.get_nowait()
                queue.task_done()
                if not old_future.done():
                    old_future.cancel()
            except asyncio.QueueEmpty:
                pass

        loop = asyncio.get_running_loop()
        future: asyncio.Future[List[CognitiveEvent]] = loop.create_future()
        await queue.put((payload, future))
        return await future

    def get_session(self, session_id: str) -> CognitiveSession:
        return self._sessions.setdefault(session_id, CognitiveSession(session_id))

    def get_session_snapshot(self, session_id: str) -> dict:
        """Return a JSON-serializable snapshot for REST endpoints."""
        session = self.get_session(session_id)
        return {
            "session_id": session_id,
            "state": session.state_engine.current_state.value,
            "state_since": session.state_engine.time_in_current_state(),
            "confidence": session.state_engine.current_confidence,
            "reason": session.state_engine.current_reason,
            "detection_count": len(session.latest_detections),
            "detections": [d.model_dump() for d in session.latest_detections],
            "behaviors": [
                {"behavior": b.behavior.value, "confidence": b.confidence, "reason": b.reason}
                for b in session.latest_behaviors
            ],
            "transitions": [
                {
                    "previous": t.previous.value,
                    "new": t.new.value,
                    "reason": t.reason,
                    "confidence": t.confidence,
                    "timestamp": t.wall_time,
                }
                for t in session.state_engine.last_n_transitions(5)
            ],
            "mode": session.demo_mode,
        }

    # ------------------------------------------------------------------
    # Worker loop
    # ------------------------------------------------------------------
    async def _worker(self, session_id: str) -> None:
        queue = self._queues[session_id]
        logger.info("[cognitive] worker started session=%s", session_id)
        while True:
            payload, future = await queue.get()
            try:
                events = await self._process(payload)
                if not future.cancelled():
                    future.set_result(events)
            except Exception as exc:
                logger.exception("[cognitive] worker error session=%s: %s", session_id, exc)
                if not future.cancelled():
                    future.set_exception(exc)
            finally:
                queue.task_done()

    async def _process(self, payload: LiveFramePayload) -> List[CognitiveEvent]:
        session = self._sessions[payload.session_id]
        events: List[CognitiveEvent] = []

        # 1) YOLO detection (in thread pool)
        loop = asyncio.get_running_loop()
        detections = await loop.run_in_executor(
            _yolo_executor,
            self._yolo.detect_from_base64,
            payload.image_base64,
        )
        session.latest_detections = detections

        # 2) Push to temporal memory
        session.memory.push(detections)

        # 3) Always emit a DETECTION event (rate-limited by frame queue)
        events.append(CognitiveEvent(
            event_type="DETECTION",
            payload={
                "session_id": payload.session_id,
                "frame_id": payload.frame_id,
                "count": len(detections),
                "labels": [d.label for d in detections],
                "detections": [d.model_dump() for d in detections],
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        ))

        # 4) Run behavior inference at most once per second
        now = time.monotonic()
        if now - session._last_behavior_tick >= 1.0:
            session._last_behavior_tick = now

            behaviors = infer_behaviors(session.memory, demo_mode=session.demo_mode)
            session.latest_behaviors = behaviors

            # 5) State engine
            transition = session.state_engine.update(behaviors)

            # 6) Reaction engine
            reaction_events = session.reaction_engine.react(
                transition=transition,
                state_engine=session.state_engine,
                behaviors=behaviors,
                memory=session.memory,
                demo_mode=session.demo_mode,
            )
            events.extend(reaction_events)

        return events
