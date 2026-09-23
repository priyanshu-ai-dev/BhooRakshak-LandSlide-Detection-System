"""
api/v1/endpoints/gis.py — Read-only GIS layer endpoints.

Endpoints
---------
  GET /api/v1/gis/layers
      Returns metadata for all available GIS layers.

  GET /api/v1/gis/layers/{layer_id}
      Returns a GeoJSON FeatureCollection for the named layer.
      Supported layer_id: "landslide-events"

  Query parameters for /layers/{layer_id}:
      bbox    : comma-separated minlon,minlat,maxlon,maxlat (EPSG:4326)
                Example: ?bbox=90.0,23.0,97.0,29.0
      limit   : max features to return (default 2000, max 5000)

Data source
-----------
  NASA Global Landslide Catalog (GLC/COOLR)
  https://catalog.data.gov/dataset/global-landslide-catalog-export
  License: U.S. Government public domain. Attribution requested.

  ⚠  This layer shows HISTORICAL REPORTED EVENTS, not a susceptibility
     surface or live warning. Do not infer current risk from this data.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.landslide_event import LandslideEvent

logger = logging.getLogger(__name__)
router = APIRouter()

# ── NER default bounding box (fallback when no bbox param supplied) ───────────
NER_LON_MIN = 88.0
NER_LON_MAX = 98.0
NER_LAT_MIN = 21.0
NER_LAT_MAX = 30.0

DEFAULT_LIMIT = 2000
MAX_LIMIT     = 5000


# ── Response models ───────────────────────────────────────────────────────────

class LayerAttribution(BaseModel):
    text: str
    url: str


class GisLayerMeta(BaseModel):
    id:            str
    name:          str
    description:   str
    geometry_type: str
    crs_epsg:      int
    feature_count: Optional[int]
    bbox:          Optional[list[float]]   # [minlon, minlat, maxlon, maxlat]
    attribution:   LayerAttribution
    data_notice:   str


class GisLayersResponse(BaseModel):
    layers: list[GisLayerMeta]


# ── Layer catalogue (Phase 1: one layer) ─────────────────────────────────────

LAYER_CATALOGUE: dict[str, dict[str, Any]] = {
    "landslide-events": {
        "name":          "Historical Landslide Events (NASA GLC)",
        "description":   (
            "Point inventory of reported landslide events in Northeast India "
            "from the NASA Global Landslide Catalog (GLC/COOLR). "
            "Covers 2007–present. Events are filtered to the NER bounding box."
        ),
        "geometry_type": "Point",
        "crs_epsg":      4326,
        "attribution": {
            "text": (
                "Kirschbaum et al. (2010) doi:10.1007/s11069-009-9401-4; "
                "Kirschbaum et al. (2015) doi:10.1016/j.geomorph.2015.03.016 "
                "— NASA/GSFC Global Landslide Catalog"
            ),
            "url": "https://catalog.data.gov/dataset/global-landslide-catalog-export",
        },
        "data_notice": (
            "HISTORICAL EVENT INVENTORY ONLY. "
            "These points show where landslides have been reported; "
            "they do NOT represent a susceptibility surface, "
            "hazard zone boundary, or live warning."
        ),
    },
}


# ── Helper: build layer metadata with live counts ─────────────────────────────

def _get_layer_meta(layer_id: str, db: Session) -> GisLayerMeta:
    spec = LAYER_CATALOGUE[layer_id]

    if layer_id == "landslide-events":
        try:
            count_row = db.execute(
                select(func.count()).select_from(LandslideEvent)
            ).scalar()
            feature_count = int(count_row) if count_row is not None else None

            # Compute actual extent from data
            if feature_count and feature_count > 0:
                extent_row = db.execute(
                    text(
                        "SELECT ST_XMin(ext), ST_YMin(ext), ST_XMax(ext), ST_YMax(ext) "
                        "FROM (SELECT ST_Extent(geom) AS ext FROM landslide_events) sub"
                    )
                ).fetchone()
                bbox = list(extent_row) if extent_row and extent_row[0] is not None else None
            else:
                bbox = None
        except Exception as exc:
            logger.warning("Could not compute layer stats for %s: %s", layer_id, exc)
            feature_count = None
            bbox = None
    else:
        feature_count = None
        bbox = None

    return GisLayerMeta(
        id=layer_id,
        name=spec["name"],
        description=spec["description"],
        geometry_type=spec["geometry_type"],
        crs_epsg=spec["crs_epsg"],
        feature_count=feature_count,
        bbox=bbox,
        attribution=LayerAttribution(**spec["attribution"]),
        data_notice=spec["data_notice"],
    )


# ── GET /api/v1/gis/layers ────────────────────────────────────────────────────

@router.get(
    "",
    response_model=GisLayersResponse,
    summary="List available GIS layers",
    description=(
        "Returns metadata for all GIS layers available in Phase 1. "
        "Use the layer `id` to request GeoJSON data from the individual layer endpoint."
    ),
    tags=["GIS"],
)
def list_layers(db: Session = Depends(get_db)) -> GisLayersResponse:
    layers = [_get_layer_meta(lid, db) for lid in LAYER_CATALOGUE]
    return GisLayersResponse(layers=layers)


# ── GET /api/v1/gis/layers/{layer_id} ─────────────────────────────────────────

@router.get(
    "/{layer_id}",
    summary="Get GeoJSON for a GIS layer",
    description=(
        "Returns a GeoJSON FeatureCollection for the requested layer. "
        "Optionally filter by bounding box with `?bbox=minlon,minlat,maxlon,maxlat`. "
        "Results are capped at the `limit` parameter (default 2000, max 5000)."
    ),
    tags=["GIS"],
    response_model=None,
)
def get_layer(
    layer_id: str,
    bbox: Optional[str] = Query(
        default=None,
        description=(
            "Spatial filter: minlon,minlat,maxlon,maxlat in EPSG:4326. "
            "Example: 90.0,23.0,97.0,29.0"
        ),
    ),
    limit: int = Query(
        default=DEFAULT_LIMIT,
        ge=1,
        le=MAX_LIMIT,
        description=f"Maximum features to return (1–{MAX_LIMIT}).",
    ),
    db: Session = Depends(get_db),
) -> dict[str, Any]:

    # ── validate layer_id ────────────────────────────────────────────────
    if layer_id not in LAYER_CATALOGUE:
        raise HTTPException(
            status_code=404,
            detail=(
                f"Layer '{layer_id}' not found. "
                f"Available layers: {list(LAYER_CATALOGUE.keys())}"
            ),
        )

    # ── parse bbox ───────────────────────────────────────────────────────
    if bbox is not None:
        try:
            parts = [float(x.strip()) for x in bbox.split(",")]
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="bbox must be four comma-separated numbers: minlon,minlat,maxlon,maxlat",
            )

        if len(parts) != 4:
            raise HTTPException(
                status_code=400,
                detail="bbox must have exactly 4 values: minlon,minlat,maxlon,maxlat",
            )

        minlon, minlat, maxlon, maxlat = parts

        if not (-180 <= minlon < maxlon <= 180):
            raise HTTPException(
                status_code=400,
                detail="bbox longitude values must satisfy -180 ≤ minlon < maxlon ≤ 180",
            )
        if not (-90 <= minlat < maxlat <= 90):
            raise HTTPException(
                status_code=400,
                detail="bbox latitude values must satisfy -90 ≤ minlat < maxlat ≤ 90",
            )
    else:
        # Default: NER bounding box
        minlon, minlat, maxlon, maxlat = NER_LON_MIN, NER_LAT_MIN, NER_LON_MAX, NER_LAT_MAX

    # ── query the database ────────────────────────────────────────────────
    try:
        rows = db.execute(
            text(
                """
                SELECT
                    id,
                    ST_X(geom)             AS lon,
                    ST_Y(geom)             AS lat,
                    event_date::text       AS event_date,
                    event_title,
                    location_description,
                    country_name,
                    country_code,
                    admin_division_name,
                    landslide_type,
                    landslide_size,
                    trigger,
                    fatalities,
                    injuries,
                    source_link,
                    source_dataset_slug
                FROM landslide_events
                WHERE ST_Within(
                    geom,
                    ST_MakeEnvelope(:minlon, :minlat, :maxlon, :maxlat, 4326)
                )
                ORDER BY event_date DESC NULLS LAST, id
                LIMIT :lim
                """
            ),
            {
                "minlon": minlon,
                "minlat": minlat,
                "maxlon": maxlon,
                "maxlat": maxlat,
                "lim":    limit,
            },
        ).fetchall()
    except Exception as exc:
        logger.error("DB query failed for layer %s: %s", layer_id, exc)
        raise HTTPException(
            status_code=500,
            detail="Database query failed. Check that the PostGIS schema and data are loaded.",
        )

    # ── build GeoJSON FeatureCollection ──────────────────────────────────
    features = []
    for row in rows:
        feature: dict[str, Any] = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [row.lon, row.lat],
            },
            "properties": {
                "id":                   row.id,
                "event_date":           row.event_date,
                "event_title":          row.event_title,
                "location_description": row.location_description,
                "country_name":         row.country_name,
                "country_code":         row.country_code,
                "admin_division_name":  row.admin_division_name,
                "landslide_type":       row.landslide_type,
                "landslide_size":       row.landslide_size,
                "trigger":              row.trigger,
                "fatalities":           row.fatalities,
                "injuries":             row.injuries,
                "source_link":          row.source_link,
                "source_dataset_slug":  row.source_dataset_slug,
            },
        }
        features.append(feature)

    spec = LAYER_CATALOGUE[layer_id]

    return {
        "type": "FeatureCollection",
        "features": features,
        "_meta": {
            "layer_id":       layer_id,
            "layer_name":     spec["name"],
            "feature_count":  len(features),
            "limit":          limit,
            "bbox_filter":    [minlon, minlat, maxlon, maxlat],
            "crs":            "EPSG:4326",
            "data_notice":    spec["data_notice"],
            "attribution":    spec["attribution"],
        },
    }
