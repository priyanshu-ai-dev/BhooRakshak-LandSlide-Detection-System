# Phase 1: GIS Foundation

This document details the first data integration phase for the NER Landslide Early Warning System.

## Selected Dataset: NASA Global Landslide Catalog (COOLR)

In Phase 1, we established a static GIS layer representing a historical inventory of reported landslide events across the globe, filtered to the Northeast India bounding box. 

* **Source**: NASA Goddard Space Flight Center — Cooperative Open Online Landslide Repository (COOLR).
* **Official URL**: [https://catalog.data.gov/dataset/global-landslide-catalog-export](https://catalog.data.gov/dataset/global-landslide-catalog-export)
* **Dataset**: Global Landslide Catalog Export (CSV).
* **Geometry**: Point data (representing approximate coordinates of reported incidents).
* **CRS**: WGS 84 / EPSG:4326.
* **License**: U.S. Government public domain work.

### Important Data Contract Notice
**This dataset is a historical event inventory only.** It is NOT a live warning system, nor does it represent a continuous spatial susceptibility raster (e.g., continuous pixel scores of landslide hazard). It purely plots locations of reported landslides in the past.

### Citation Required
When using this dataset, the following attribution must be maintained:
> Kirschbaum, D.B. et al. (2010) Natural Hazards 52(3):561-575 doi:10.1007/s11069-009-9401-4
> Kirschbaum, D.B. et al. (2015) Geomorphology doi:10.1016/j.geomorph.2015.03.016

## Import Procedure

To import the data into the local PostGIS database:

1. Start the database service: `docker compose up db -d`
2. Ensure the Phase 1 schema migrations have run automatically via `database/init/02_phase1_gis_schema.sql`.
3. Download the `Global_Landslide_Catalog_Export.csv` from the data.gov URL.
4. Place it at `ingestion/data/Global_Landslide_Catalog_Export.csv`.
5. Run the importer script from the project root:
   ```bash
   # Make sure dependencies are installed (psycopg2-binary)
   pip install -r ingestion/requirements.txt
   
   # Run the script
   python ingestion/import_nasa_glc.py
   ```
   *The import is idempotent and safe to run multiple times.*

## API Endpoints

The backend provides read-only GeoJSON endpoints serving this data.

* `GET /api/v1/gis/layers`
  Returns metadata for all available GIS layers (e.g., `landslide-events`).
  
* `GET /api/v1/gis/layers/landslide-events`
  Returns a GeoJSON `FeatureCollection` for the NASA GLC dataset.
  **Supported Query Parameters:**
  * `bbox` (Optional): Filter spatially using `minlon,minlat,maxlon,maxlat`.
  * `limit` (Optional): Maximum number of features (default 2000).

## Frontend Implementation

The React frontend integrates MapLibre GL to render the GeoJSON features as styled circle layers. 
* A color classification based on `landslide_size` (catastrophic, very large, large, medium, small/unknown) is applied.
* Clicking a circle opens a popup with event details (date, type, trigger, description).
* A side panel checkbox allows users to toggle the visibility of the layer.
* The map displays an attribution control acknowledging the data source.

## Next Recommended Milestone (Phase 2)
The next phase (Phase 2) will focus on ingesting live environmental data (Rainfall or Soil Moisture API feeds) or building field reporting tools. Phase 1 provides the solid base schema (PostGIS, GeoAlchemy2, React-MapLibre integration) for those future vector/raster layers.
