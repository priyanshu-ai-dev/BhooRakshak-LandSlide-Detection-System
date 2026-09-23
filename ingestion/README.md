# ingestion/ — Data Ingestion Pipelines

**Status: Phase 0 — Not yet implemented.**

This module will contain scheduled / event-driven pipelines that pull external data into the PostGIS database:

| Pipeline | Source | Cadence |
|---|---|---|
| Rainfall | IMD / GPM IMERG | Hourly |
| Soil moisture | NASA SMAP | Daily |
| Seismic | NCS / USGS | Real-time |
| DEM / slope | SRTM / ALOS | One-time |
| NDVI | Sentinel-2 / Landsat | 5-day |

**Tech stack:** Python · requests · rasterio · geopandas · APScheduler / Celery

> Ingestion logic is completely separate from the FastAPI backend. Pipelines write directly to the database; the backend reads from it.
