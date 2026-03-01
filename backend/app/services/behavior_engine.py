"""Behavior Inference Engine – derives high-level behaviors from temporal memory.

Rules-based inference that runs every ~1 second (called by the cognitive
pipeline, NOT per-frame).  Outputs a ranked list of detected behaviors.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum
from typing import List

from app.services.temporal_memory import TemporalMemory

logger = logging.getLogger(__name__)

WORKSTATION_OBJECTS = frozenset({
    "laptop", "keyboard", "mouse", "monitor", "cell phone",
    "book", "remote", "tv", "screen", "bottle", "cup",
})

PHONE_LABELS = frozenset({"cell phone"})


class Behavior(str, Enum):
    WORKING = "WORKING"
    PHONE_USAGE = "PHONE_USAGE"
    ACTIVE_MOVEMENT = "ACTIVE_MOVEMENT"
    ROOM_EMPTY = "ROOM_EMPTY"
    ANOMALY = "ANOMALY"
    IDLE = "IDLE"


@dataclass
class BehaviorResult:
    behavior: Behavior
    confidence: float  # 0–1
    reason: str


def infer_behaviors(memory: TemporalMemory, demo_mode: str = "workspace") -> List[BehaviorResult]:
    """Return a list of inferred behaviors, highest-confidence first."""
    results: List[BehaviorResult] = []

    # ----- ROOM_EMPTY -----
    if not memory.person_present and memory.person_absent_seconds > 10:
        results.append(BehaviorResult(
            behavior=Behavior.ROOM_EMPTY,
            confidence=min(1.0, 0.6 + memory.person_absent_seconds / 60),
            reason=f"No person detected for {memory.person_absent_seconds:.0f}s.",
        ))

    # ----- PHONE_USAGE -----
    phone_duration = max(memory.label_continuous_seconds(l) for l in PHONE_LABELS) if PHONE_LABELS & set(memory.object_tracks) else 0

    if memory.person_present and phone_duration > 3:
        results.append(BehaviorResult(
            behavior=Behavior.PHONE_USAGE,
            confidence=min(1.0, 0.5 + phone_duration / 20),
            reason=f"Phone detected continuously for {phone_duration:.1f}s while person present.",
        ))

    # ----- WORKING -----
    recent = memory.recent_label_set(seconds=5.0)
    workstation_count = len(recent & WORKSTATION_OBJECTS)
    if memory.person_present and workstation_count >= 1 and memory.motion_score < 0.6 and memory.person_continuous_seconds > 8:
        results.append(BehaviorResult(
            behavior=Behavior.WORKING,
            confidence=min(1.0, 0.5 + workstation_count * 0.1 + memory.person_continuous_seconds / 120),
            reason=f"Person at workstation ({workstation_count} desk objects) for {memory.person_continuous_seconds:.0f}s, low movement.",
        ))

    # ----- ACTIVE_MOVEMENT -----
    if memory.person_present and memory.motion_score > 0.5:
        results.append(BehaviorResult(
            behavior=Behavior.ACTIVE_MOVEMENT,
            confidence=min(1.0, memory.motion_score),
            reason=f"Frequent scene changes detected (motion={memory.motion_score:.2f}).",
        ))

    # ----- ANOMALY (Security mode) -----
    if demo_mode == "security":
        # New object appearing suddenly (present < 3 frames in last 10s but absent before)
        for label, track in memory.object_tracks.items():
            if label == "person":
                continue
            recent_count = memory.frame_count_for(label, seconds=5.0)
            total_count = track.total_frames
            if recent_count > 0 and total_count < 6 and track.continuous_duration < 3:
                results.append(BehaviorResult(
                    behavior=Behavior.ANOMALY,
                    confidence=0.65,
                    reason=f"New object '{label}' appeared suddenly in security mode.",
                ))
                break  # one anomaly is enough

        # Multiple persons
        person_count = memory.frame_count_for("person", seconds=3.0)
        # If person detected in many recent frames, check if there are multiple boxes
        recent_frames = [f for f in memory.frames if f.timestamp >= (memory.frames[-1].timestamp - 3.0)] if memory.frames else []
        for f in recent_frames:
            person_boxes = [d for d in f.detections if d.label == "person"]
            if len(person_boxes) > 1:
                results.append(BehaviorResult(
                    behavior=Behavior.ANOMALY,
                    confidence=0.8,
                    reason=f"Multiple persons ({len(person_boxes)}) detected in security mode.",
                ))
                break

    # ----- IDLE (fallback) -----
    if memory.person_present and not results:
        results.append(BehaviorResult(
            behavior=Behavior.IDLE,
            confidence=0.4,
            reason="Person present, no specific behavior pattern detected.",
        ))

    # Sort by confidence descending
    results.sort(key=lambda r: r.confidence, reverse=True)
    return results
