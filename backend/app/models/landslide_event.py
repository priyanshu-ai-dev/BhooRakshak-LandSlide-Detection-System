"""
app/models/landslide_event.py — SQLAlchemy ORM model for landslide_events.

Maps to the table created by database/init/02_phase1_gis_schema.sql.

Data source: NASA Global Landslide Catalog (GLC/COOLR)
  https://catalog.data.gov/dataset/global-landslide-catalog-export
License: U.S. Government public domain work. Attribution requested.
"""

from __future__ import annotations

import datetime
from typing import Optional

from geoalchemy2 import Geometry  # type: ignore[import]
from sqlalchemy import BigInteger, Date, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class LandslideEvent(Base):
    """
    Historical landslide event point from the NASA GLC/COOLR inventory.

    ⚠️  This is NOT a susceptibility map or live warning layer.
        It represents reported events at approximate point locations.
    """

    __tablename__ = "landslide_events"

    # Primary key — NASA GLC event_id
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    # PostGIS geometry: EPSG:4326 point (lon, lat)
    geom: Mapped[object] = mapped_column(
        Geometry(geometry_type="POINT", srid=4326), nullable=False
    )

    # Source traceability
    source_dataset_slug: Mapped[str] = mapped_column(
        Text, nullable=False, default="nasa-glc"
    )

    # Temporal
    event_date: Mapped[Optional[datetime.date]] = mapped_column(Date, nullable=True)
    event_date_raw: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Identity
    event_title: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    location_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    country_name: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    country_code: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    admin_division_name: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Classification
    landslide_type: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    landslide_size: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    trigger: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Impact
    fatalities: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    injuries: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Source link
    source_link: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return (
            f"<LandslideEvent id={self.id} "
            f"title={self.event_title!r} "
            f"date={self.event_date} "
            f"size={self.landslide_size}>"
        )
