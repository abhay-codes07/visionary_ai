from typing import Literal

from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import StreamingResponse

from app.api.deps import get_vision_service
from app.core.config import get_settings
from app.schemas.vision import (
    VisionAnalyzeRequest,
    VisionAnalyzeResponse,
    VisionCapabilitiesResponse,
    VisionQuestionRequest,
    VisionQuestionResponse,
    VisionStreamChunk,
    VisionUploadResponse,
)
from app.services.storage_service import StorageService
from app.services.streaming_service import StreamingService
from app.services.vision_service import VisionService

router = APIRouter(prefix="/vision")
storage_service = StorageService()
streaming_service = StreamingService()
settings = get_settings()


@router.post("/analyze", response_model=VisionAnalyzeResponse)
async def analyze_vision(
    payload: VisionAnalyzeRequest,
    service: VisionService = Depends(get_vision_service),
) -> VisionAnalyzeResponse:
    return await service.analyze(payload)


@router.post("/analyze/stream")
async def stream_vision_analysis(
    payload: VisionAnalyzeRequest,
    service: VisionService = Depends(get_vision_service),
) -> StreamingResponse:
    analysis = await service.analyze(payload)
    events = await streaming_service.stream_analysis(analysis.request_id, analysis.summary)

    async def event_generator():
        for idx, event in enumerate(events):
            chunk = VisionStreamChunk(request_id=analysis.request_id, token=event.content, index=idx)
            yield f"data: {chunk.model_dump_json()}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.get("/capabilities", response_model=VisionCapabilitiesResponse)
async def get_vision_capabilities() -> VisionCapabilitiesResponse:
    return VisionCapabilitiesResponse(
        supported_media_types=["image", "video", "webcam"],
        supported_transports=["rest", "websocket"],
        supports_streaming=True,
        model=settings.openai_model,
        openai_enabled=settings.openai_enabled,
        fallback_mode=settings.openai_fallback_to_stub,
    )


@router.post("/question", response_model=VisionQuestionResponse)
async def ask_vision_question(
    payload: VisionQuestionRequest,
    service: VisionService = Depends(get_vision_service),
) -> VisionQuestionResponse:
    return await service.answer_question(payload)


@router.post("/question/stream")
async def stream_vision_question(
    payload: VisionQuestionRequest,
    service: VisionService = Depends(get_vision_service),
) -> StreamingResponse:
    answer = await service.answer_question(payload)
    events = await streaming_service.stream_answer(answer.request_id, answer.answer)

    async def event_generator():
        for idx, event in enumerate(events):
            chunk = VisionStreamChunk(request_id=answer.request_id, token=event.content, index=idx)
            yield f"data: {chunk.model_dump_json()}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.post("/upload", response_model=VisionUploadResponse)
async def upload_media(
    media_type: Literal["image", "video", "webcam"] = Form(...),
    file: UploadFile = File(...),
) -> VisionUploadResponse:
    return await storage_service.save_upload(file, media_type)
