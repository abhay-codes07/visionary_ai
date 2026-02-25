from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Visionary Agent Protocol API"
    app_env: str = "development"
    api_v1_prefix: str = "/api/v1"
    openai_api_key: str = "replace-me"
    openai_model: str = "gpt-4.1-mini"
    websocket_path: str = "/ws"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
