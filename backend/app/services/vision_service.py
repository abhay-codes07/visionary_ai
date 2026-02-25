from datetime import datetime, UTC
from uuid import uuid4

from app.core.config import Settings, get_settings
from app.core.errors import InvalidInputError, ServiceUnavailableError
from app.integrations.openai_vision_client import OpenAIVisionClient
from app.schemas.vision import (
    VisionAnalyzeRequest,
    VisionAnalyzeResponse,
    VisionDetection,
    VisionQuestionRequest,
    VisionQuestionResponse,
)


class VisionService:
    def __init__(self, openai_client: OpenAIVisionClient | None = None, settings: Settings | None = None) -> None:
        self._openai_client = openai_client
        self._settings = settings or get_settings()

    async def analyze(self, payload: VisionAnalyzeRequest) -> VisionAnalyzeResponse:
        if not payload.prompt.strip():
            raise InvalidInputError("Prompt cannot be empty.")

        request_id = str(uuid4())
        detections = self._mock_detections(payload.media_type)
        summary = await self._resolve_summary(payload, detections_count=len(detections))
        return VisionAnalyzeResponse(
            request_id=request_id,
            media_type=payload.media_type,
            summary=summary,
            detections=detections,
            generated_at=datetime.now(UTC),
        )

    async def answer_question(self, payload: VisionQuestionRequest) -> VisionQuestionResponse:
        if not payload.question.strip():
            raise InvalidInputError("Question cannot be empty.")

        answer = await self._resolve_question_answer(payload)
        return VisionQuestionResponse(
            request_id=payload.request_id,
            answer=answer,
            generated_at=datetime.now(UTC),
        )

    @staticmethod
    def _mock_detections(media_type: str) -> list[VisionDetection]:
        base = [
            VisionDetection(label="person", confidence=0.98, description="Primary subject in frame."),
            VisionDetection(label="screen", confidence=0.91, description="Display device detected."),
            VisionDetection(label="workspace", confidence=0.87, description="Indoor operational environment."),
        ]
        if media_type == "video":
            base.append(
                VisionDetection(
                    label="motion-event", confidence=0.89, description="Temporal change detected across frames."
                )
            )
        return base

    async def _resolve_summary(self, payload: VisionAnalyzeRequest, detections_count: int) -> str:
        if self._openai_client is not None:
            try:
                ai_result = await self._openai_client.analyze_media(
                    media_type=payload.media_type,
                    prompt=payload.prompt,
                    source_uri=payload.source_uri,
                )
                if ai_result.summary.strip():
                    return ai_result.summary
                if not self._settings.openai_fallback_to_stub:
                    raise ServiceUnavailableError("AI provider returned empty summary.")
            except Exception as exc:
                if not self._settings.openai_fallback_to_stub:
                    raise ServiceUnavailableError("AI provider request failed.") from exc

        return (
            f"Processed {payload.media_type} input with {detections_count} detected scene elements. "
            f"Prompt focus: {payload.prompt}"
        )

    async def _resolve_question_answer(self, payload: VisionQuestionRequest) -> str:
        if self._openai_client is not None:
            try:
                ai_result = await self._openai_client.analyze_media(
                    media_type="image",
                    prompt=payload.question,
                    source_uri=None,
                )
                if ai_result.summary.strip():
                    return ai_result.summary
                if not self._settings.openai_fallback_to_stub:
                    raise ServiceUnavailableError("AI provider returned empty answer.")
            except Exception as exc:
                if not self._settings.openai_fallback_to_stub:
                    raise ServiceUnavailableError("AI provider question request failed.") from exc

        return (
            f"Request {payload.request_id}: Based on the analyzed scene, "
            f"the most likely interpretation is that key entities are stable and trackable."
        )
