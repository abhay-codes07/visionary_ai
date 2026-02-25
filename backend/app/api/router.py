from fastapi import APIRouter

from app.api.routes import health, realtime, vision

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(vision.router, tags=["vision"])
api_router.include_router(realtime.router, tags=["realtime"])
