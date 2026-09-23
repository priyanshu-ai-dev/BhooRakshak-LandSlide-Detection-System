"""
api/v1/endpoints/health.py — GET /api/v1/health

Returns a structured JSON response confirming the backend is reachable.
Phase 1: includes a db_status field from a lightweight DB ping.
"""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from app.core.config import settings
from app.core.database import ping_db

router = APIRouter()


class HealthResponse(BaseModel):
    status: str
    version: str
    service: str
    phase: str
    db_status: str


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
    db_ok = await __import__("asyncio").get_event_loop().run_in_executor(None, ping_db)
    return HealthResponse(
        status="ok",
        version=settings.app_version,
        service=settings.app_name,
        phase="1",
        db_status="ok" if db_ok else "unreachable",
    )
