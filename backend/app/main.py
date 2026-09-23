"""
app/main.py — FastAPI application factory.

Responsibilities:
- Create and configure the FastAPI app instance.
- Register CORS middleware.
- Mount versioned API routers.
- Define startup / shutdown lifecycle logging.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import router as v1_router
from app.core.config import settings

logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s — %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:  # noqa: ARG001
    logger.info("━━━ Starting %s v%s ━━━", settings.app_name, settings.app_version)
    yield
    logger.info("━━━ Shutting down %s ━━━", settings.app_name)


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "AI-based Landslide Early Warning and Risk Monitoring System "
        "for Northeast India (NER). Phase 1 — GIS Foundation. "
        "Serves historical landslide event inventory from the NASA Global Landslide "
        "Catalog (GLC/COOLR) as a read-only GeoJSON API. "
        "This is NOT a live warning system."
    ),
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ──────────────────────────────────────────────────────────────────
app.include_router(v1_router, prefix="/api/v1")


# ── Root redirect ─────────────────────────────────────────────────────────────
@app.get("/", include_in_schema=False)
async def root() -> dict[str, str]:
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/api/v1/health",
    }
