from datetime import datetime, UTC
from uuid import uuid4

from app.core.errors import InvalidInputError
from app.schemas.vision import (
    VisionAnalyzeRequest,
    VisionAnalyzeResponse,
    VisionDetection,
    VisionQuestionRequest,
    VisionQuestionResponse,
)


class VisionService:
    async def analyze(self, payload: VisionAnalyzeRequest) -> VisionAnalyzeResponse:
        if not payload.prompt.strip():
            raise InvalidInputError("Prompt cannot be empty.")

        request_id = str(uuid4())
        detections = self._mock_detections(payload.media_type)
        summary = (
            f"Processed {payload.media_type} input with {len(detections)} detected scene elements. "
            f"Prompt focus: {payload.prompt}"
        )
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

        answer = (
            f"Request {payload.request_id}: Based on the analyzed scene, "
            f"the most likely interpretation is that key entities are stable and trackable."
        )
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
