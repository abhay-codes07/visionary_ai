from __future__ import annotations

from datetime import UTC, datetime

from app.schemas.live import LiveStreamEvent


class StreamService:
    async def tokenize(self, text: str, session_id: str, frame_id: str | None = None) -> list[LiveStreamEvent]:
        words = text.split()
        if not words:
            return [
                LiveStreamEvent(
                    type="token",
                    session_id=session_id,
                    frame_id=frame_id,
                    content="",
                    timestamp=datetime.now(UTC),
                )
            ]

        chunks = [" ".join(words[i : i + 2]) for i in range(0, len(words), 2)]
        return [
            LiveStreamEvent(
                type="token",
                session_id=session_id,
                frame_id=frame_id,
                content=chunk,
                timestamp=datetime.now(UTC),
            )
            for chunk in chunks
        ]
