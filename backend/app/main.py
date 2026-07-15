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
from app.api.auth import router as auth_router
from app.api.chat import router as chat_router
from app.api.cross_media import router as cross_media_router
from app.api.digest import router as digest_router
from app.api.feedback import router as feedback_router
from app.api.health import router as health_router
from app.api.memory import router as memory_router
from app.api.preferences import router as preferences_router
from app.api.recommendations import router as recommendations_router
from app.core.config import get_settings
from app.core.scheduler import start_scheduler, stop_scheduler

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
    start_scheduler()
    yield
    stop_scheduler()
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
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(chat_router, prefix="/api/chat", tags=["chat"])
app.include_router(feedback_router, prefix="/api/feedback", tags=["feedback"])
app.include_router(memory_router, prefix="/api/memory", tags=["memory"])
app.include_router(preferences_router, prefix="/api/preferences", tags=["preferences"])
app.include_router(recommendations_router, prefix="/api/recommendations", tags=["recommendations"])
app.include_router(cross_media_router, prefix="/api/recommendations", tags=["cross-media"])
app.include_router(digest_router, prefix="/api/digest", tags=["digest"])
