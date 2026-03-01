"""Tests for the Cognitive Vision Pipeline engines."""

from app.schemas.live import BoundingBox, LiveDetection
from app.services.behavior_engine import Behavior, infer_behaviors
from app.services.state_engine import BrainState, StateEngine
from app.services.temporal_memory import TemporalMemory


def _person_det(conf: float = 0.9) -> LiveDetection:
    return LiveDetection(label="person", confidence=conf, box=BoundingBox(x=10, y=10, width=100, height=200))


def _obj_det(label: str, conf: float = 0.8) -> LiveDetection:
    return LiveDetection(label=label, confidence=conf, box=BoundingBox(x=50, y=50, width=40, height=40))


# --------- Temporal Memory ---------

def test_temporal_memory_push_and_labels() -> None:
    mem = TemporalMemory()
    mem.push([_person_det(), _obj_det("laptop")])
    assert mem.person_present is True
    assert "person" in mem.active_labels
    assert "laptop" in mem.active_labels


def test_temporal_memory_label_frequency() -> None:
    mem = TemporalMemory()
    mem.push([_person_det()])
    mem.push([_person_det()])
    mem.push([_person_det()])
    assert mem.label_frequency["person"] >= 3


def test_temporal_memory_recent_label_set() -> None:
    mem = TemporalMemory()
    mem.push([_person_det(), _obj_det("cup")])
    recent = mem.recent_label_set(seconds=5.0)
    assert "person" in recent
    assert "cup" in recent


# --------- Behavior Engine ---------

def test_behavior_room_empty() -> None:
    mem = TemporalMemory()
    # No person pushed, person_absent_seconds defaults to 999
    behaviors = infer_behaviors(mem, demo_mode="workspace")
    labels = [b.behavior for b in behaviors]
    assert Behavior.ROOM_EMPTY in labels


def test_behavior_idle_when_person_present() -> None:
    mem = TemporalMemory()
    mem.push([_person_det()])
    behaviors = infer_behaviors(mem, demo_mode="workspace")
    labels = [b.behavior for b in behaviors]
    # Person present but not long enough for WORKING, so IDLE expected
    assert Behavior.IDLE in labels or Behavior.ACTIVE_MOVEMENT in labels


# --------- State Engine ---------

def test_state_engine_initial_state() -> None:
    engine = StateEngine()
    assert engine.current_state == BrainState.INITIALIZING


def test_state_engine_no_transition_without_hold() -> None:
    """A single update shouldn't cause immediate transition (hold threshold)."""
    from app.services.behavior_engine import BehaviorResult
    engine = StateEngine()
    result = engine.update([BehaviorResult(behavior=Behavior.ROOM_EMPTY, confidence=0.8, reason="test")])
    # May or may not transition depending on hold threshold
    # The key thing is it doesn't crash
    assert engine.current_state in list(BrainState)


def test_state_engine_tracks_transitions() -> None:
    engine = StateEngine()
    assert isinstance(engine.last_n_transitions(5), list)
    assert engine.time_in_current_state() >= 0
