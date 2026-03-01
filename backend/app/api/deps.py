from functools import lru_cache

from app.core.config import get_settings
from app.integrations.openai_vision_client import OpenAIVisionClient
from app.services.cognitive_pipeline import CognitivePipeline
from app.services.live_stream_service import LiveStreamService
from app.services.stream_service import StreamService
from app.services.vision_service import VisionService


def get_vision_service() -> VisionService:
    settings = get_settings()
    return VisionService(openai_client=get_openai_vision_client(), settings=settings)


@lru_cache
def get_openai_vision_client() -> OpenAIVisionClient | None:
    settings = get_settings()
    if not settings.openai_enabled:
        return None
    return OpenAIVisionClient(settings=settings)


@lru_cache
def get_live_stream_service() -> LiveStreamService:
    return LiveStreamService()


@lru_cache
def get_stream_service() -> StreamService:
    return StreamService()


@lru_cache
def get_cognitive_pipeline() -> CognitivePipeline:
    return CognitivePipeline()
