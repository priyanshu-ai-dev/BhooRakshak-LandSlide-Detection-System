/**
 * api/gis.ts — Client functions for the GIS endpoints.
 */
import { API_BASE_URL } from '../config'
import type { GisLayersResponse, LandslideEventsFeatureCollection } from '../types/gis'

/**
 * Fetch metadata for all available GIS layers.
 */
export async function fetchGisLayers(): Promise<GisLayersResponse> {
  const url = `${API_BASE_URL}/api/v1/gis/layers`
  const response = await fetch(url)

  if (!response.ok) {
    throw new Error(`Failed to fetch GIS layers — HTTP ${response.status} ${response.statusText}`)
  }

  return response.json() as Promise<GisLayersResponse>
}

/**
 * Fetch the historical landslide events GeoJSON feature collection.
 * @param bbox Optional bounding box: minlon,minlat,maxlon,maxlat
 */
export async function fetchLandslideEvents(bbox?: string): Promise<LandslideEventsFeatureCollection> {
  const url = new URL(`${API_BASE_URL}/api/v1/gis/layers/landslide-events`)
  if (bbox) {
    url.searchParams.append('bbox', bbox)
  }

  const response = await fetch(url.toString())

  if (!response.ok) {
    throw new Error(`Failed to fetch landslide events — HTTP ${response.status} ${response.statusText}`)
  }

  return response.json() as Promise<LandslideEventsFeatureCollection>
}
