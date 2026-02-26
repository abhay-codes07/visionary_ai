from datetime import datetime, timezone

from app.schemas.realtime import RealtimeOutboundMessage


class StreamingService:
    async def stream_analysis(self, request_id: str, summary: str) -> list[RealtimeOutboundMessage]:
        parts = self._split(summary, words_per_chunk=3)
        return [
            RealtimeOutboundMessage(
                type="token",
                request_id=request_id,
                content=part,
                timestamp=datetime.now(timezone.utc),
            )
            for part in parts
        ]

    async def stream_answer(self, request_id: str, answer: str) -> list[RealtimeOutboundMessage]:
        parts = self._split(answer, words_per_chunk=2)
        return [
            RealtimeOutboundMessage(
                type="token",
                request_id=request_id,
                content=part,
                timestamp=datetime.now(timezone.utc),
            )
            for part in parts
        ]

    @staticmethod
    def _split(text: str, words_per_chunk: int) -> list[str]:
        words = text.split()
        if not words:
            return [""]
        size = max(1, words_per_chunk)
        slices = [" ".join(words[idx : idx + size]) for idx in range(0, len(words), size)]
        return slices[:28]

