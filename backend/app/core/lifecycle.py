from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    # Service bootstrap hooks (logger, metrics, clients) are attached in later phases.
    yield
