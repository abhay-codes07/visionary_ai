from datetime import UTC, datetime

from app.schemas.realtime import RealtimeOutboundMessage


class StreamingService:
    async def stream_analysis(self, request_id: str, summary: str) -> list[RealtimeOutboundMessage]:
        parts = self._split(summary, 3)
        return [
            RealtimeOutboundMessage(
                type="token",
                request_id=request_id,
                content=part,
                timestamp=datetime.now(UTC),
            )
            for part in parts
        ]

    async def stream_answer(self, request_id: str, answer: str) -> list[RealtimeOutboundMessage]:
        parts = self._split(answer, 4)
        return [
            RealtimeOutboundMessage(
                type="token",
                request_id=request_id,
                content=part,
                timestamp=datetime.now(UTC),
            )
            for part in parts
        ]

    @staticmethod
    def _split(text: str, chunks: int) -> list[str]:
        words = text.split()
        if not words:
            return [""]
        size = max(1, len(words) // chunks)
        slices = [" ".join(words[idx : idx + size]) for idx in range(0, len(words), size)]
        return slices[:chunks] if len(slices) > chunks else slices
