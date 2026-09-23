-- Phase 1: GIS Foundation — Landslide Event Inventory Schema
-- Executed automatically by the postgis/postgis Docker image on first boot
-- via /docker-entrypoint-initdb.d/ (files run in alphabetical order).
--
-- Data source: NASA Global Landslide Catalog (GLC/COOLR)
-- https://catalog.data.gov/dataset/global-landslide-catalog-export
-- Citation: Kirschbaum et al. 2010 & 2015 (DOI: 10.1007/s11069-009-9401-4)
-- License: U.S. Government public domain work. Attribution requested.

-- ─────────────────────────────────────────────────────────────────────────────
-- 1. GIS Source Dataset Registry
--    Tracks provenance of every imported GIS layer. One row per source.
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS gis_source_datasets (
    id                  SERIAL PRIMARY KEY,
    slug                VARCHAR(64)  NOT NULL UNIQUE,
    name                TEXT         NOT NULL,
    description         TEXT,
    source_url          TEXT         NOT NULL,
    license             TEXT         NOT NULL,
    attribution_text    TEXT         NOT NULL,
    version_or_date     VARCHAR(64),
    coverage            TEXT,
    geometry_type       VARCHAR(32)  NOT NULL,  -- e.g. 'Point', 'Polygon', 'Raster'
    crs_epsg            INTEGER      NOT NULL DEFAULT 4326,
    notes               TEXT,
    imported_at         TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

-- Seed the NASA GLC source record
INSERT INTO gis_source_datasets (
    slug,
    name,
    description,
    source_url,
    license,
    attribution_text,
    version_or_date,
    coverage,
    geometry_type,
    crs_epsg,
    notes
) VALUES (
    'nasa-glc',
    'NASA Global Landslide Catalog (GLC/COOLR)',
    'A point inventory of rainfall-triggered landslide events compiled by NASA GSFC '
    'from news reports, academic publications, and disaster databases. '
    'Covers 2007-present. This is a catalogue of REPORTED events, not a '
    'continuous susceptibility surface.',
    'https://catalog.data.gov/dataset/global-landslide-catalog-export',
    'U.S. Government public domain work. Attribution requested.',
    'Kirschbaum, D.B. et al. (2010) Natural Hazards 52(3):561-575 '
    'doi:10.1007/s11069-009-9401-4 | '
    'Kirschbaum, D.B. et al. (2015) Geomorphology doi:10.1016/j.geomorph.2015.03.016',
    '2007–present (export date varies)',
    'Global; NER India subset (bbox 88°E–98°E, 21°N–30°N) stored here',
    'Point',
    4326,
    'NOT a susceptibility map. Events are point locations of recorded incidents; '
    'spatial precision varies by report quality. Do not use as a live warning system.'
) ON CONFLICT (slug) DO NOTHING;


-- ─────────────────────────────────────────────────────────────────────────────
-- 2. Landslide Events Table
--    Stores historical point events from the NASA GLC, filtered to NER India.
--    Coordinates are stored in EPSG:4326 (WGS 84).
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS landslide_events (
    -- Primary key — NASA GLC event_id (numeric, assigned by NASA)
    id                  BIGINT PRIMARY KEY,

    -- Geometry: EPSG:4326 point (lon, lat)
    geom                GEOMETRY(Point, 4326) NOT NULL,

    -- Source traceability
    source_dataset_slug VARCHAR(64) NOT NULL REFERENCES gis_source_datasets(slug)
                        DEFAULT 'nasa-glc',

    -- Temporal
    event_date          DATE,
    event_date_raw      TEXT,        -- preserve the original string from CSV

    -- Identity
    event_title         TEXT,
    location_description TEXT,
    country_name        TEXT,
    country_code        CHAR(2),
    admin_division_name TEXT,

    -- Classification
    landslide_type      TEXT,        -- landslide / mudslide / debris_flow / rock_fall / etc.
    landslide_size      TEXT,        -- catastrophic / very_large / large / medium / small / unknown
    trigger             TEXT,        -- rain / earthquake / continuous_rain / etc.

    -- Impact
    fatalities          INTEGER,
    injuries            INTEGER,

    -- Source metadata
    source_link         TEXT,        -- URL of the original report, if available

    -- Import bookkeeping
    imported_at         TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE landslide_events IS
    'Historical landslide event points from the NASA Global Landslide Catalog (GLC/COOLR). '
    'NER India subset (bounding box 88°E–98°E, 21°N–30°N). '
    'This is a catalogue of REPORTED events, not a susceptibility or live warning layer.';

COMMENT ON COLUMN landslide_events.geom IS
    'Point geometry in EPSG:4326 (WGS 84). Coordinates from NASA GLC lat/lon fields.';

COMMENT ON COLUMN landslide_events.landslide_size IS
    'Size classification from NASA GLC: catastrophic, very_large, large, medium, small, or unknown.';


-- ─────────────────────────────────────────────────────────────────────────────
-- 3. Spatial Index
--    GiST index on the geometry column — required for efficient ST_Within /
--    ST_Intersects / bounding-box spatial queries in the API.
-- ─────────────────────────────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS landslide_events_geom_idx
    ON landslide_events USING GIST (geom);

-- Supporting indexes for common filter/sort operations
CREATE INDEX IF NOT EXISTS landslide_events_date_idx
    ON landslide_events (event_date DESC NULLS LAST);

CREATE INDEX IF NOT EXISTS landslide_events_size_idx
    ON landslide_events (landslide_size);

CREATE INDEX IF NOT EXISTS landslide_events_source_idx
    ON landslide_events (source_dataset_slug);


-- ─────────────────────────────────────────────────────────────────────────────
-- 4. Verification
-- ─────────────────────────────────────────────────────────────────────────────
DO $$
BEGIN
    RAISE NOTICE 'Phase 1 schema: gis_source_datasets and landslide_events tables created.';
    RAISE NOTICE 'Spatial index (GiST) on landslide_events.geom created.';
    RAISE NOTICE 'Run ingestion/import_nasa_glc.py to populate landslide_events from NASA GLC CSV.';
END;
$$;
