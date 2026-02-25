from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.errors import VisionaryError


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(VisionaryError)
    async def visionary_error_handler(_: Request, exc: VisionaryError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": {"code": exc.code, "message": exc.message}},
        )
