"""
app/models/__init__.py — ORM model registry.

Import all model modules here so SQLAlchemy's metadata is populated
before any create_all() or migration tool call.
"""

from app.models.landslide_event import LandslideEvent  # noqa: F401
