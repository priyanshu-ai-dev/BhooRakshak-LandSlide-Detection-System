"""
core/database.py — SQLAlchemy engine and session factory.

Phase 0: synchronous engine with psycopg2.
The session factory is wired up here so future phases only need to add models
and call get_db() as a FastAPI dependency.

No DB queries are made in Phase 0; this module exists to validate configuration
and ensure the structure is ready for Phase 1.
"""

from __future__ import annotations

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings


engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,   # reconnect automatically after network hiccup
    echo=settings.debug,  # log SQL when DEBUG=true
)

SessionLocal: sessionmaker[Session] = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


class Base(DeclarativeBase):
    """Base class for all ORM models. Import and subclass in each model file."""


def get_db():  # type: ignore[return]
    """
    FastAPI dependency that yields a database session.
    Usage:
        @router.get("/example")
        def example(db: Session = Depends(get_db)):
            ...
    """
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def ping_db() -> bool:
    """
    Attempt a lightweight DB round-trip.
    Returns True on success, False on failure.
    Used by future health-check enhancements.
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
