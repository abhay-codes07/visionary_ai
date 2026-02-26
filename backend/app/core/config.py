from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Visionary Agent Protocol API"
    app_env: str = "development"
    api_v1_prefix: str = "/api/v1"
    openai_api_key: str = "replace-me"
    openai_model: str = "gpt-4.1-mini"
    openai_enabled: bool = False
    openai_timeout_seconds: float = 30.0
    openai_max_retries: int = 2
    openai_retry_backoff_seconds: float = 0.75
    openai_fallback_to_stub: bool = True
    yolo_model: str = "yolov8n.pt"
    yolo_confidence_threshold: float = 0.35
    visionagents_enabled: bool = False
    live_frame_max_fps: int = 8
    live_frame_queue_size: int = 4
    websocket_path: str = "/ws"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
