from datetime import datetime

from pydantic import BaseModel


class SystemStatusResponse(BaseModel):
    status: str
    started_at: datetime
    uptime_seconds: int
    openai_enabled: bool
    fallback_mode: bool
