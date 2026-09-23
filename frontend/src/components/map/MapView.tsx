import { useEffect, useRef, useState } from 'react'
import maplibregl from 'maplibre-gl'
import type { StyleSpecification } from 'maplibre-gl'
import 'maplibre-gl/dist/maplibre-gl.css'

import SusceptibilityLegend from './SusceptibilityLegend'
import { fetchLandslideEvents } from '../../api/gis'

/** Geographic center of Northeast India (lon, lat) */
const NE_INDIA_CENTER: [number, number] = [93.5, 26.0]
const INITIAL_ZOOM = 6

/**
 * OSM raster tile style — no API key required.
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

interface MapViewProps {
  showHistoricalEvents: boolean
}

/**
 * MapView — full-size MapLibre GL map centred on Northeast India.
 * Phase 1: Renders historical landslide events GeoJSON.
 */
export default function MapView({ showHistoricalEvents }: MapViewProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const mapRef = useRef<maplibregl.Map | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState<boolean>(true)

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

    map.on('load', () => {
      // Add empty GeoJSON source first
      map.addSource('landslide-events', {
        type: 'geojson',
        data: { type: 'FeatureCollection', features: [] },
        attribution: 'NASA Global Landslide Catalog'
      })

      // Add circle layer
      map.addLayer({
        id: 'landslide-events-points',
        type: 'circle',
        source: 'landslide-events',
        layout: {
          'visibility': showHistoricalEvents ? 'visible' : 'none'
        },
        paint: {
          'circle-radius': [
            'interpolate', ['linear'], ['zoom'],
            5, 4,
            12, 12
          ],
          'circle-color': [
            'match',
            ['get', 'landslide_size'],
            'catastrophic', '#dc2626',
            'very_large', '#ea580c',
            'large', '#d97706',
            'medium', '#65a30d',
            'small', '#6b7280',
            /* other */ '#6b7280'
          ],
          'circle-stroke-width': 1,
          'circle-stroke-color': 'rgba(255, 255, 255, 0.5)',
          'circle-opacity': 0.8
        }
      })

      // Popup on click
      map.on('click', 'landslide-events-points', (e) => {
        if (!e.features || e.features.length === 0) return
        
        const props = e.features[0].properties
        const coordinates = (e.features[0].geometry as any).coordinates.slice()

        while (Math.abs(e.lngLat.lng - coordinates[0]) > 180) {
          coordinates[0] += e.lngLat.lng > coordinates[0] ? 360 : -360
        }

        const html = `
          <div class="text-sm p-1 text-gray-800">
            <strong class="block mb-1 text-base">${props.event_title || 'Unnamed Event'}</strong>
            <div class="space-y-1">
              <p><strong>Date:</strong> ${props.event_date || 'Unknown'}</p>
              <p><strong>Location:</strong> ${props.admin_division_name || ''}, ${props.country_name || ''}</p>
              <p><strong>Type:</strong> ${props.landslide_type || 'Unknown'} (${props.landslide_size || 'Unknown'} size)</p>
              <p><strong>Trigger:</strong> ${props.trigger || 'Unknown'}</p>
            </div>
          </div>
        `

        new maplibregl.Popup()
          .setLngLat(coordinates)
          .setHTML(html)
          .addTo(map)
      })

      map.on('mouseenter', 'landslide-events-points', () => {
        map.getCanvas().style.cursor = 'pointer'
      })
      
      map.on('mouseleave', 'landslide-events-points', () => {
        map.getCanvas().style.cursor = ''
      })

      // Fetch data
      fetchLandslideEvents()
        .then(data => {
          (map.getSource('landslide-events') as maplibregl.GeoJSONSource).setData(data)
          setLoading(false)
        })
        .catch(err => {
          console.error('Failed to load map data:', err)
          setError(err.message)
          setLoading(false)
        })
    })

    mapRef.current = map

    return () => {
      map.remove()
      mapRef.current = null
    }
  }, []) // Empty dependency array ensures we only initialize once

  // React to toggle changes
  useEffect(() => {
    if (!mapRef.current || !mapRef.current.isStyleLoaded()) return
    const visibility = showHistoricalEvents ? 'visible' : 'none'
    if (mapRef.current.getLayer('landslide-events-points')) {
      mapRef.current.setLayoutProperty('landslide-events-points', 'visibility', visibility)
    }
  }, [showHistoricalEvents])

  return (
    <div className="relative w-full h-full">
      {/* Map canvas */}
      <div ref={containerRef} className="w-full h-full" />

      {/* Overlays */}
      <div className="absolute top-3 left-3 z-10 flex items-center gap-2 bg-gray-900/80 backdrop-blur-sm px-3 py-2 rounded-lg text-xs text-gray-300 pointer-events-none select-none">
        <span className="text-orange-400">📍</span>
        <span>Northeast India</span>
        <span className="mx-1 text-gray-600">·</span>
        <span className="text-gray-500 italic">Phase 1</span>
      </div>

      {loading && (
        <div className="absolute top-14 left-3 z-10 bg-gray-900/80 backdrop-blur-sm px-3 py-2 rounded-lg text-xs text-gray-300 pointer-events-none select-none flex items-center gap-2">
          <div className="w-3 h-3 rounded-full border-2 border-orange-400 border-t-transparent animate-spin" />
          Loading GIS Data...
        </div>
      )}

      {error && (
        <div className="absolute top-14 left-3 z-10 bg-red-900/80 backdrop-blur-sm px-3 py-2 rounded-lg text-xs text-red-200 pointer-events-none select-none">
          Failed to load GIS data: {error}
        </div>
      )}

      {showHistoricalEvents && <SusceptibilityLegend />}
    </div>
  )
}
