-- Phase 0: Enable PostGIS extension
-- This file is executed automatically by the postgis/postgis Docker image
-- on first container start via /docker-entrypoint-initdb.d/

CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;

-- Verify
DO $$
BEGIN
  RAISE NOTICE 'PostGIS version: %', PostGIS_Version();
END;
$$;
