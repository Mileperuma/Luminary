"""FastAPI entry point for Luminary.

This is the skeleton — feature routes will be added in /backend/app/api/*
as the sprints progress (see docs/03_Project_Plan.docx Section 5).
"""

import logging

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

app = FastAPI(
    title=settings.APP_NAME,
    version=__version__,
    description="AI-powered cross-media recommendation assistant for books, articles, and movies.",
    docs_url="/docs",
    redoc_url="/redoc",
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


@app.on_event("startup")
def on_startup() -> None:
    log.info("Luminary backend starting (env=%s)", settings.APP_ENV)


@app.on_event("shutdown")
def on_shutdown() -> None:
    log.info("Luminary backend shutting down")
