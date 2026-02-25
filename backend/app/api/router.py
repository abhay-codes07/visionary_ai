from fastapi import APIRouter

from app.api.routes import health, realtime, system, vision

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(system.router, tags=["system"])
api_router.include_router(vision.router, tags=["vision"])
api_router.include_router(realtime.router, tags=["realtime"])
