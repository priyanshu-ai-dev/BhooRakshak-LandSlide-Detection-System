import { useEffect, useRef } from 'react'
import maplibregl from 'maplibre-gl'
import type { StyleSpecification } from 'maplibre-gl'

/** Geographic center of Northeast India (lon, lat) */
const NE_INDIA_CENTER: [number, number] = [93.5, 26.0]
const INITIAL_ZOOM = 6

/**
 * OSM raster tile style — no API key required.
 * Phase 1 will overlay vector risk layers on top of this basemap.
 */
const BASE_STYLE: StyleSpecification = {
  version: 8,
  sources: {
    osm: {
      type: 'raster',
      tiles: ['https://tile.openstreetmap.org/{z}/{x}/{y}.png'],
      tileSize: 256,
      attribution:
        '© <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a> contributors',
      maxzoom: 19,
    },
  },
  layers: [
    {
      id: 'osm-tiles',
      type: 'raster',
      source: 'osm',
    },
  ],
}

/**
 * MapView — full-size MapLibre GL map centred on Northeast India.
 *
 * Phase 0: basemap only, no risk data.
 * Future phases will add GeoJSON / vector-tile sources for susceptibility,
 * rainfall, and alert layers.
 */
export default function MapView() {
  const containerRef = useRef<HTMLDivElement>(null)
  const mapRef = useRef<maplibregl.Map | null>(null)

  useEffect(() => {
    if (mapRef.current !== null || containerRef.current === null) return

    const map = new maplibregl.Map({
      container: containerRef.current,
      style: BASE_STYLE,
      center: NE_INDIA_CENTER,
      zoom: INITIAL_ZOOM,
    })

    map.addControl(new maplibregl.NavigationControl(), 'top-right')
    map.addControl(new maplibregl.ScaleControl({ unit: 'metric' }), 'bottom-left')
    map.addControl(
      new maplibregl.AttributionControl({ compact: true }),
      'bottom-right',
    )

    mapRef.current = map

    return () => {
      map.remove()
      mapRef.current = null
    }
  }, [])

  return (
    <div className="relative w-full h-full">
      {/* Map canvas */}
      <div ref={containerRef} className="w-full h-full" />

      {/* Phase badge — visible overlay, non-interactive */}
      <div className="absolute top-3 left-3 z-10 flex items-center gap-2 bg-gray-900/80 backdrop-blur-sm px-3 py-2 rounded-lg text-xs text-gray-300 pointer-events-none select-none">
        <span className="text-orange-400">📍</span>
        <span>Northeast India</span>
        <span className="mx-1 text-gray-600">·</span>
        <span className="text-gray-500 italic">Phase 0 — no risk layers loaded</span>
      </div>
    </div>
  )
}
