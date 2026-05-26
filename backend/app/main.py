"""FastAPI entry point for Luminary.

This is the skeleton — feature routes will be added in /backend/app/api/*
as the sprints progress (see docs/03_Project_Plan.docx Section 5).
"""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.api.health import router as health_router
from app.core.config import get_settings

settings = get_settings()

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
log = logging.getLogger("luminary")


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Startup / shutdown hooks for the app.

    Uses the modern lifespan pattern (FastAPI >= 0.93). Anything that needs
    to run once at boot (DB connection check, warm caches) goes before the
    `yield`; anything that needs to run on shutdown goes after.
    """
    log.info("Luminary backend starting (env=%s)", settings.APP_ENV)
    yield
    log.info("Luminary backend shutting down")


app = FastAPI(
    title=settings.APP_NAME,
    version=__version__,
    description="AI-powered cross-media recommendation assistant for books, articles, and movies.",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers (feature routers will be added here as they land)
app.include_router(health_router, prefix="/api", tags=["health"])
