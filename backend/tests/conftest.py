"""
tests/conftest.py — Pytest fixtures for unit and integration tests.

Strategy
--------
The GIS endpoint tests use a mock database session so they never require
a live PostgreSQL instance. The mocked session returns clearly labelled
synthetic test fixture data.

⚠  All data returned by these fixtures is SYNTHETIC TEST DATA.
   It does NOT represent real landslide locations or events.
   Fixture coordinates are chosen inside the NER bounding box but
   must not be interpreted as actual historical events.
"""

from __future__ import annotations

from typing import Any, Generator
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app


# ─────────────────────────────────────────────────────────────────────────────
# Synthetic test fixture rows
# ⚠  SYNTHETIC TEST DATA — not real events
# ─────────────────────────────────────────────────────────────────────────────
class _FakeRow:
    """Mimics a SQLAlchemy Row returned by text() queries."""

    def __init__(self, **kwargs: Any) -> None:
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __iter__(self):
        return iter(vars(self).values())

    def __getitem__(self, idx):
        return list(vars(self).values())[idx]


SYNTHETIC_EVENTS: list[_FakeRow] = [
    # ⚠ SYNTHETIC TEST FIXTURE — not a real event
    _FakeRow(
        id=99001,
        lon=91.7,      # Within NER bbox: Assam region (fictional)
        lat=26.1,
        event_date="2020-07-15",
        event_title="[TEST FIXTURE] Fictional landslide event A",
        location_description="Synthetic location — test only",
        country_name="India",
        country_code="IN",
        admin_division_name="Assam (SYNTHETIC)",
        landslide_type="landslide",
        landslide_size="large",
        trigger="rain",
        fatalities=0,
        injuries=0,
        source_link="",
        source_dataset_slug="nasa-glc",
    ),
    # ⚠ SYNTHETIC TEST FIXTURE — not a real event
    _FakeRow(
        id=99002,
        lon=93.0,      # Within NER bbox: Nagaland region (fictional)
        lat=25.5,
        event_date="2021-08-20",
        event_title="[TEST FIXTURE] Fictional landslide event B",
        location_description="Synthetic location — test only",
        country_name="India",
        country_code="IN",
        admin_division_name="Nagaland (SYNTHETIC)",
        landslide_type="debris_flow",
        landslide_size="medium",
        trigger="continuous_rain",
        fatalities=None,
        injuries=None,
        source_link="",
        source_dataset_slug="nasa-glc",
    ),
]

SYNTHETIC_EXTENT_ROW = _FakeRow(**{"0": 91.7, "1": 25.5, "2": 93.0, "3": 26.1})


# ─────────────────────────────────────────────────────────────────────────────
# Mock DB session fixture
# ─────────────────────────────────────────────────────────────────────────────

def _make_mock_db() -> MagicMock:
    mock_db = MagicMock()

    def execute_side_effect(stmt, params=None, **kwargs):
        result = MagicMock()
        stmt_str = str(stmt)

        if "ST_Extent" in stmt_str:
            # Layer metadata extent query
            result.fetchone.return_value = SYNTHETIC_EXTENT_ROW
        elif "ST_Within" in stmt_str:
            # GeoJSON feature query
            result.fetchall.return_value = SYNTHETIC_EVENTS
        else:
            # count() query
            result.scalar.return_value = len(SYNTHETIC_EVENTS)

        return result

    mock_db.execute.side_effect = execute_side_effect
    return mock_db


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    """TestClient with DB mocked — no live PostGIS required."""
    from app.core.database import get_db

    mock_db = _make_mock_db()

    def override_get_db():
        yield mock_db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
