"""Reaction Engine – emits alerts and contextual summaries on state changes.

Generates WebSocket events: STATE_CHANGE, ALERT, SUMMARY.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List, Optional

from app.services.behavior_engine import Behavior, BehaviorResult
from app.services.state_engine import BrainState, StateEngine, StateTransition
from app.services.temporal_memory import TemporalMemory

logger = logging.getLogger(__name__)


@dataclass
class CognitiveEvent:
    """Generic event produced by the reaction engine."""

    event_type: str  # STATE_CHANGE | ALERT | SUMMARY
    payload: dict


class ReactionEngine:
    """Generates events when state changes or periodic summaries are due."""

    def __init__(self) -> None:
        self._last_summary_time: float = 0.0
        self._summary_interval: float = 10.0  # seconds

    def react(
        self,
        transition: Optional[StateTransition],
        state_engine: StateEngine,
        behaviors: List[BehaviorResult],
        memory: TemporalMemory,
        demo_mode: str,
    ) -> List[CognitiveEvent]:
        import time

        events: List[CognitiveEvent] = []

        # 1) STATE_CHANGE event
        if transition is not None:
            events.append(CognitiveEvent(
                event_type="STATE_CHANGE",
                payload={
                    "previous_state": transition.previous.value,
                    "new_state": transition.new.value,
                    "reason": transition.reason,
                    "confidence": round(transition.confidence, 3),
                    "timestamp": transition.wall_time,
                },
            ))

            # 2) Mode-specific ALERT
            alert = self._check_alert(transition, state_engine, demo_mode)
            if alert:
                events.append(alert)

        # 3) Periodic SUMMARY
        now = time.monotonic()
        if now - self._last_summary_time >= self._summary_interval:
            self._last_summary_time = now
            events.append(self._build_summary(state_engine, behaviors, memory, demo_mode))

        return events

    # ------------------------------------------------------------------
    # Alert rules
    # ------------------------------------------------------------------
    @staticmethod
    def _check_alert(
        transition: StateTransition,
        state_engine: StateEngine,
        demo_mode: str,
    ) -> Optional[CognitiveEvent]:
        new = transition.new
        now_str = datetime.now(timezone.utc).isoformat()

        if demo_mode == "workspace":
            if new == BrainState.DISTRACTED:
                return CognitiveEvent(
                    event_type="ALERT",
                    payload={
                        "level": "warning",
                        "title": "Productivity Warning",
                        "message": "Phone usage detected during workspace session.",
                        "state": new.value,
                        "timestamp": now_str,
                    },
                )
            if new == BrainState.AWAY:
                return CognitiveEvent(
                    event_type="ALERT",
                    payload={
                        "level": "info",
                        "title": "Session Paused",
                        "message": "User has left the workspace. Session paused.",
                        "state": new.value,
                        "timestamp": now_str,
                    },
                )

        if demo_mode == "security":
            if new == BrainState.SUSPICIOUS:
                return CognitiveEvent(
                    event_type="ALERT",
                    payload={
                        "level": "critical",
                        "title": "Security Alert",
                        "message": transition.reason,
                        "state": new.value,
                        "timestamp": now_str,
                    },
                )

        return None

    # ------------------------------------------------------------------
    # Summary builder
    # ------------------------------------------------------------------
    @staticmethod
    def _build_summary(
        state_engine: StateEngine,
        behaviors: List[BehaviorResult],
        memory: TemporalMemory,
        demo_mode: str,
    ) -> CognitiveEvent:
        duration = state_engine.time_in_current_state()
        state = state_engine.current_state.value
        objects = ", ".join(sorted(memory.active_labels)) or "none"

        parts: list[str] = []

        if state_engine.current_state == BrainState.FOCUSED:
            parts.append(f"User has been focused for {_fmt_duration(duration)}.")
        elif state_engine.current_state == BrainState.DISTRACTED:
            parts.append(f"Phone usage detected during {demo_mode} session.")
        elif state_engine.current_state == BrainState.AWAY:
            parts.append(f"Room empty for {_fmt_duration(memory.person_absent_seconds)}.")
        elif state_engine.current_state == BrainState.SUSPICIOUS:
            parts.append("Anomaly detected — monitoring active.")
        elif state_engine.current_state == BrainState.ACTIVE:
            parts.append(f"Active movement detected for {_fmt_duration(duration)}.")
        else:
            parts.append(f"Currently {state.lower()} for {_fmt_duration(duration)}.")

        # Object context
        if objects != "none":
            parts.append(f"Visible objects: {objects}.")

        # Behaviour detail
        if behaviors:
            top = behaviors[0]
            if top.reason and top.reason not in parts[0]:
                parts.append(top.reason)

        # No anomalies note
        if state_engine.current_state not in (BrainState.SUSPICIOUS,):
            parts.append("No anomalies.")

        return CognitiveEvent(
            event_type="SUMMARY",
            payload={
                "state": state,
                "duration_seconds": round(duration, 1),
                "confidence": round(state_engine.current_confidence, 3),
                "text": " ".join(parts),
                "active_objects": sorted(memory.active_labels),
                "mode": demo_mode,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )


def _fmt_duration(seconds: float) -> str:
    if seconds < 60:
        return f"{seconds:.0f} seconds"
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes}m {secs}s"
