"""Temporal Memory Layer – rolling window of detection history per session.

Maintains 30–60 seconds of frame-level object data so that the Behavior
Engine can reason about *patterns over time* rather than treating each frame
independently.
"""

from __future__ import annotations

import logging
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Set

from app.schemas.live import LiveDetection

logger = logging.getLogger(__name__)

# How many seconds of history to keep.
MEMORY_WINDOW_SECONDS = 60.0


@dataclass
class FrameSnapshot:
    """Detection snapshot for a single frame."""

    timestamp: float  # time.monotonic()
    labels: List[str]
    detections: List[LiveDetection]


@dataclass
class ObjectTrack:
    """Accumulated statistics for a single label."""

    label: str
    first_seen: float = 0.0
    last_seen: float = 0.0
    total_frames: int = 0
    # How long the object has been *continuously* present (resets on gap > 2s).
    continuous_duration: float = 0.0


@dataclass
class TemporalMemory:
    """Rolling memory for one session."""

    frames: List[FrameSnapshot] = field(default_factory=list)
    object_tracks: Dict[str, ObjectTrack] = field(default_factory=dict)
    # High-level summaries updated each tick
    person_present: bool = False
    person_continuous_seconds: float = 0.0
    person_absent_seconds: float = 0.0
    active_labels: Set[str] = field(default_factory=set)
    label_frequency: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    motion_score: float = 0.0  # 0=static, 1=very active (simple heuristic)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def push(self, detections: List[LiveDetection]) -> None:
        """Record one frame of detections and update statistics."""
        now = time.monotonic()
        labels = [d.label for d in detections]
        self.frames.append(FrameSnapshot(timestamp=now, labels=labels, detections=detections))
        self._prune(now)
        self._update_tracks(labels, now)
        self._update_summaries(now)

    def seconds_since_last_person(self) -> float:
        track = self.object_tracks.get("person")
        if track is None:
            return 999.0
        return time.monotonic() - track.last_seen

    def label_continuous_seconds(self, label: str) -> float:
        track = self.object_tracks.get(label)
        if track is None:
            return 0.0
        return track.continuous_duration

    def recent_label_set(self, seconds: float = 5.0) -> Set[str]:
        cutoff = time.monotonic() - seconds
        result: Set[str] = set()
        for f in reversed(self.frames):
            if f.timestamp < cutoff:
                break
            result.update(f.labels)
        return result

    def frame_count_for(self, label: str, seconds: float = 10.0) -> int:
        cutoff = time.monotonic() - seconds
        return sum(1 for f in self.frames if f.timestamp >= cutoff and label in f.labels)

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------
    def _prune(self, now: float) -> None:
        cutoff = now - MEMORY_WINDOW_SECONDS
        while self.frames and self.frames[0].timestamp < cutoff:
            self.frames.pop(0)

    def _update_tracks(self, labels: List[str], now: float) -> None:
        seen = set(labels)
        for label in seen:
            self.label_frequency[label] += 1
            track = self.object_tracks.get(label)
            if track is None:
                track = ObjectTrack(label=label, first_seen=now, last_seen=now, total_frames=1)
                self.object_tracks[label] = track
            else:
                gap = now - track.last_seen
                track.total_frames += 1
                if gap < 2.0:
                    track.continuous_duration += gap
                else:
                    track.continuous_duration = 0.0
                track.last_seen = now

        # Decay continuous duration for labels NOT seen this frame.
        for label, track in self.object_tracks.items():
            if label not in seen:
                gap = now - track.last_seen
                if gap > 2.0:
                    track.continuous_duration = 0.0

    def _update_summaries(self, now: float) -> None:
        self.active_labels = self.recent_label_set(seconds=3.0)
        person_track = self.object_tracks.get("person")
        if person_track and (now - person_track.last_seen) < 2.0:
            self.person_present = True
            self.person_continuous_seconds = person_track.continuous_duration
            self.person_absent_seconds = 0.0
        else:
            self.person_present = False
            self.person_continuous_seconds = 0.0
            self.person_absent_seconds = now - person_track.last_seen if person_track else 999.0

        # Simple motion heuristic – count how many different label-sets we saw
        # in the last 3 seconds.  More variety → more motion.
        recent = [frozenset(f.labels) for f in self.frames if f.timestamp >= now - 3.0]
        unique = len(set(recent))
        self.motion_score = min(1.0, unique / max(len(recent), 1))
