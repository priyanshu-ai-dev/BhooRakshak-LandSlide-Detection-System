"""
core/config.py — Application settings loaded from environment variables / .env file.

Uses pydantic-settings so every variable is type-safe and validated at startup.
The env_file tuple lets the backend be started from *either* the project root
or the backend/ directory.
"""

from __future__ import annotations

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        # Try .env in CWD first, then parent directory (covers running
        # `uvicorn app.main:app` from backend/ or from project root).
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ──────────────────────────────────────────────────────────
    app_name: str = "NER Landslide EWS Backend"
    app_version: str = "0.1.0"
    debug: bool = False

    # ── Database ─────────────────────────────────────────────────────────────
    database_url: str = (
        "postgresql://postgres:changeme_in_production@localhost:5432/ner_landslide"
    )

    # ── CORS ─────────────────────────────────────────────────────────────────
    # Accepts a comma-separated string in the env var, e.g.:
    #   CORS_ORIGINS=http://localhost:5173,http://localhost:3000
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _parse_cors(cls, v: object) -> object:
        # If already a list (e.g. injected programmatically), leave it alone.
        if isinstance(v, list):
            return v
        return v  # returned as str; split happens in the property below

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    # ── Server ───────────────────────────────────────────────────────────────
    backend_port: int = 8000


# Single module-level instance — import this everywhere.
settings = Settings()
