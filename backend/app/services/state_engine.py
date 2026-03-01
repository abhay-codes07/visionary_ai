"""State Engine – maps behaviors to brain states with debounce/threshold logic.

State changes only after a behavior is consistently detected for a threshold
duration, preventing flickering.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

from app.services.behavior_engine import Behavior, BehaviorResult

logger = logging.getLogger(__name__)


class BrainState(str, Enum):
    FOCUSED = "FOCUSED"
    DISTRACTED = "DISTRACTED"
    AWAY = "AWAY"
    SUSPICIOUS = "SUSPICIOUS"
    ACTIVE = "ACTIVE"
    IDLE = "IDLE"
    INITIALIZING = "INITIALIZING"


# Mapping from Behavior → BrainState
BEHAVIOR_STATE_MAP: Dict[Behavior, BrainState] = {
    Behavior.WORKING: BrainState.FOCUSED,
    Behavior.PHONE_USAGE: BrainState.DISTRACTED,
    Behavior.ROOM_EMPTY: BrainState.AWAY,
    Behavior.ANOMALY: BrainState.SUSPICIOUS,
    Behavior.ACTIVE_MOVEMENT: BrainState.ACTIVE,
    Behavior.IDLE: BrainState.IDLE,
}

# Minimum seconds a candidate state must be dominant before we commit the
# transition.  This prevents rapid flickering.
STATE_HOLD_THRESHOLD: Dict[BrainState, float] = {
    BrainState.FOCUSED: 3.0,
    BrainState.DISTRACTED: 2.0,
    BrainState.AWAY: 5.0,
    BrainState.SUSPICIOUS: 1.0,
    BrainState.ACTIVE: 2.0,
    BrainState.IDLE: 4.0,
}
DEFAULT_HOLD = 3.0


@dataclass
class StateTransition:
    previous: BrainState
    new: BrainState
    reason: str
    confidence: float
    timestamp: float  # time.monotonic()
    wall_time: str  # ISO-8601


@dataclass
class StateEngine:
    """Per-session state tracker."""

    current_state: BrainState = BrainState.INITIALIZING
    current_state_since: float = field(default_factory=time.monotonic)
    current_confidence: float = 0.0
    current_reason: str = "Session starting."

    # Candidate that must hold for threshold before committing
    _candidate_state: BrainState = BrainState.INITIALIZING
    _candidate_since: float = field(default_factory=time.monotonic)
    _candidate_confidence: float = 0.0
    _candidate_reason: str = ""

    transitions: List[StateTransition] = field(default_factory=list)

    def update(self, behaviors: List[BehaviorResult]) -> Optional[StateTransition]:
        """Process latest behavior list.  Returns a StateTransition if the
        brain state changed, otherwise None."""
        now = time.monotonic()

        if not behaviors:
            return None

        top = behaviors[0]
        proposed = BEHAVIOR_STATE_MAP.get(top.behavior, BrainState.IDLE)

        # Is this the same candidate as before?
        if proposed == self._candidate_state:
            # Update confidence / reason
            self._candidate_confidence = top.confidence
            self._candidate_reason = top.reason
        else:
            # New candidate – reset timer
            self._candidate_state = proposed
            self._candidate_since = now
            self._candidate_confidence = top.confidence
            self._candidate_reason = top.reason

        # Already in this state? Just refresh metadata
        if proposed == self.current_state:
            self.current_confidence = top.confidence
            self.current_reason = top.reason
            return None

        # Check if candidate has held long enough
        hold = STATE_HOLD_THRESHOLD.get(proposed, DEFAULT_HOLD)
        if now - self._candidate_since >= hold:
            return self._commit_transition(proposed, top, now)

        return None

    def time_in_current_state(self) -> float:
        return time.monotonic() - self.current_state_since

    def last_n_transitions(self, n: int = 5) -> List[StateTransition]:
        return self.transitions[-n:]

    # ------------------------------------------------------------------

    def _commit_transition(self, new_state: BrainState, top: BehaviorResult, now: float) -> StateTransition:
        from datetime import datetime, timezone

        transition = StateTransition(
            previous=self.current_state,
            new=new_state,
            reason=top.reason,
            confidence=top.confidence,
            timestamp=now,
            wall_time=datetime.now(timezone.utc).isoformat(),
        )
        logger.info(
            "[state] %s → %s  (confidence=%.2f, reason=%s)",
            self.current_state.value,
            new_state.value,
            top.confidence,
            top.reason,
        )
        self.current_state = new_state
        self.current_state_since = now
        self.current_confidence = top.confidence
        self.current_reason = top.reason
        self.transitions.append(transition)
        # Keep max 50 transitions
        if len(self.transitions) > 50:
            self.transitions = self.transitions[-50:]
        return transition
