"""
api/v1/endpoints/health.py — GET /api/v1/health

Returns a structured JSON response confirming the backend is reachable.
Phase 0: no DB check. A db_status field is reserved for Phase 1.
"""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from app.core.config import settings

router = APIRouter()


class HealthResponse(BaseModel):
    status: str
    version: str
    service: str
    phase: str


@router.get(
    "",
    response_model=HealthResponse,
    summary="Backend health check",
    description=(
        "Returns HTTP 200 with service metadata when the backend is running. "
        "No authentication required."
    ),
)
async def health_check() -> HealthResponse:
    return HealthResponse(
        status="ok",
        version=settings.app_version,
        service=settings.app_name,
        phase="0",
    )
