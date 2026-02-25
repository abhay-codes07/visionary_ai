from datetime import datetime, UTC

from fastapi import APIRouter

from app.core.config import get_settings
from app.core.state import app_state
from app.schemas.system import SystemStatusResponse

router = APIRouter(prefix="/system")


@router.get("/status", response_model=SystemStatusResponse)
async def system_status() -> SystemStatusResponse:
    settings = get_settings()
    now = datetime.now(UTC)
    uptime = max(0, int((now - app_state.started_at).total_seconds()))
    return SystemStatusResponse(
        status="ok",
        started_at=app_state.started_at,
        uptime_seconds=uptime,
        openai_enabled=settings.openai_enabled,
        fallback_mode=settings.openai_fallback_to_stub,
    )
