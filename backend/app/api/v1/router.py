"""
api/v1/router.py — Aggregates all v1 endpoint routers.

Add new routers here as phases progress.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.endpoints import gis, health

router = APIRouter()

# ── Phase 0 ──────────────────────────────────────────────────────────────────
router.include_router(health.router, prefix="/health", tags=["Health"])

# ── Phase 1 ──────────────────────────────────────────────────────────────────
router.include_router(gis.router, prefix="/gis/layers", tags=["GIS"])

# ── Phase 2+ (planned) ───────────────────────────────────────────────────────
# router.include_router(rainfall.router, prefix="/rainfall", tags=["Rainfall"])
# router.include_router(alerts.router, prefix="/alerts", tags=["Alerts"])
