/**
 * types/gis.ts — TypeScript interfaces for the GIS API responses.
 *
 * Must stay in sync with:
 *   backend/app/api/v1/endpoints/gis.py
 */

// ── Layer metadata ──────────────────────────────────────────────────────────

export interface GisLayerAttribution {
  text: string
  url: string
}

export interface GisLayerMeta {
  id: string
  name: string
  description: string
  geometry_type: string
  crs_epsg: number
  feature_count: number | null
  bbox: [number, number, number, number] | null  // [minlon, minlat, maxlon, maxlat]
  attribution: GisLayerAttribution
  data_notice: string
}

export interface GisLayersResponse {
  layers: GisLayerMeta[]
}

// ── Landslide event feature properties ─────────────────────────────────────

export interface LandslideEventProperties {
  id: number
  event_date: string | null
  event_title: string | null
  location_description: string | null
  country_name: string | null
  country_code: string | null
  admin_division_name: string | null
  landslide_type: string | null
  landslide_size: LandslideSize | null
  trigger: string | null
  fatalities: number | null
  injuries: number | null
  source_link: string | null
  source_dataset_slug: string
}

/** Normalised size classes from NASA GLC */
export type LandslideSize =
  | 'catastrophic'
  | 'very_large'
  | 'large'
  | 'medium'
  | 'small'
  | 'unknown'

// ── GeoJSON types ───────────────────────────────────────────────────────────

export interface LandslideEventFeature {
  type: 'Feature'
  geometry: {
    type: 'Point'
    coordinates: [number, number]  // [lon, lat] — EPSG:4326
  }
  properties: LandslideEventProperties
}

export interface GisFeatureCollectionMeta {
  layer_id: string
  layer_name: string
  feature_count: number
  limit: number
  bbox_filter: [number, number, number, number]
  crs: string
  data_notice: string
  attribution: GisLayerAttribution
}

export interface LandslideEventsFeatureCollection {
  type: 'FeatureCollection'
  features: LandslideEventFeature[]
  _meta: GisFeatureCollectionMeta
}
