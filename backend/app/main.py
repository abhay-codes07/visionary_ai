from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import get_settings
from app.core.lifecycle import lifespan


def create_application() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)
    app.include_router(api_router, prefix=settings.api_v1_prefix)
    return app


app = create_application()
