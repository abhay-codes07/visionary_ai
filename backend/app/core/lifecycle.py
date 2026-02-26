from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import AsyncIterator

from fastapi import FastAPI

from app.core.state import app_state


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    # Service bootstrap hooks (logger, metrics, clients) are attached in later phases.
    app_state.started_at = datetime.now(timezone.utc)
    yield

