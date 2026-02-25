from dataclasses import dataclass
from typing import Literal

from openai import AsyncOpenAI

from app.core.config import Settings

MediaType = Literal["image", "video", "webcam"]


@dataclass(frozen=True)
class OpenAIVisionResult:
    summary: str


class OpenAIVisionClient:
    def __init__(self, settings: Settings) -> None:
        self._model = settings.openai_model
        self._client = AsyncOpenAI(api_key=settings.openai_api_key)

    async def analyze_media(self, media_type: MediaType, prompt: str, source_uri: str | None = None) -> OpenAIVisionResult:
        content: list[dict[str, str]] = [{"type": "input_text", "text": prompt}]

        if source_uri:
            content.append({"type": "input_image", "image_url": source_uri})

        response = await self._client.responses.create(
            model=self._model,
            input=[{"role": "user", "content": content}],
            metadata={"media_type": media_type},
        )
        summary = (getattr(response, "output_text", "") or "").strip()
        return OpenAIVisionResult(summary=summary or "No summary returned by model.")
