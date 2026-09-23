import { useState } from 'react'
import MapView from '../map/MapView'
import HealthBanner from '../status/HealthBanner'

/** Sidebar layer/tool entry */
interface SidebarItem {
  id: string
  label: string
  availableFrom: string
  active?: boolean
  isToggleable?: boolean
}

const FUTURE_RISK_LAYERS: SidebarItem[] = [
  { id: 'rainfall', label: 'Rainfall', availableFrom: 'Phase 2' },
  { id: 'soil-moisture', label: 'Soil Moisture', availableFrom: 'Phase 2' },
  { id: 'seismic', label: 'Seismic Activity', availableFrom: 'Phase 2' },
]

const TOOLS: SidebarItem[] = [
  { id: 'reports', label: 'Field Reports', availableFrom: 'Phase 2' },
  { id: 'alerts', label: 'Alert Log', availableFrom: 'Phase 2' },
  { id: 'ml', label: 'ML Inference', availableFrom: 'Phase 3' },
]

function DisabledItem({ item }: { item: SidebarItem }) {
  return (
    <div className="flex items-center gap-2 px-3 py-2 rounded bg-gray-700/50 text-sm text-gray-500 cursor-not-allowed select-none">
      <span className="w-2 h-2 rounded-full bg-gray-600 shrink-0" />
      <span className="flex-1 truncate">{item.label}</span>
      <span className="text-[10px] text-gray-600 shrink-0">{item.availableFrom}</span>
    </div>
  )
}

/**
 * DashboardLayout — three-panel shell:
 *   ┌─────────────────────────────────────────┐
 *   │  Top nav bar  (title + health banner)   │
 *   ├───────────┬─────────────────────────────┤
 *   │  Sidebar  │         Map canvas          │
 *   │  (layers) │                             │
 *   └───────────┴─────────────────────────────┘
 */
export default function DashboardLayout() {
  const [showHistoricalEvents, setShowHistoricalEvents] = useState(true)

  return (
    <div className="flex flex-col h-screen bg-gray-900 text-white overflow-hidden">
      {/* ── Top Navigation Bar ────────────────────────────────────────── */}
      <header className="flex items-center justify-between px-6 py-3 bg-gray-800 border-b border-gray-700 shrink-0">
        <div className="flex items-center gap-3">
          <span className="text-2xl" aria-hidden="true">⛰️</span>
          <div>
            <h1 className="text-base font-bold leading-tight tracking-wide">
              NER Landslide EWS
            </h1>
            <p className="text-[11px] text-gray-400 leading-tight">
              Northeast India Early Warning System
            </p>
          </div>
        </div>

        <HealthBanner />
      </header>

      {/* ── Main Body ─────────────────────────────────────────────────── */}
      <div className="flex flex-1 overflow-hidden">
        {/* ── Left Sidebar ────────────────────────────────────────────── */}
        <aside className="w-60 bg-gray-800 border-r border-gray-700 flex flex-col p-4 gap-5 shrink-0 overflow-y-auto">
          {/* Active Risk Layers (Phase 1) */}
          <section>
            <h2 className="text-[10px] font-semibold uppercase tracking-widest text-gray-400 mb-2">
              Data Layers
            </h2>
            <div className="space-y-1.5">
              <label className="flex items-center gap-3 px-3 py-2 rounded bg-gray-700/70 hover:bg-gray-700 cursor-pointer transition-colors select-none text-sm">
                <input 
                  type="checkbox" 
                  className="rounded border-gray-500 bg-gray-800 text-orange-500 focus:ring-orange-500 focus:ring-offset-gray-800"
                  checked={showHistoricalEvents}
                  onChange={(e) => setShowHistoricalEvents(e.target.checked)}
                />
                <span className="flex-1 truncate text-gray-200">Historical Events</span>
              </label>
            </div>
          </section>

          {/* Future Risk Layers */}
          <section>
            <h2 className="text-[10px] font-semibold uppercase tracking-widest text-gray-500 mb-2">
              Future Risk Layers
            </h2>
            <div className="space-y-1.5">
              {FUTURE_RISK_LAYERS.map((item) => (
                <DisabledItem key={item.id} item={item} />
              ))}
            </div>
          </section>

          {/* Tools */}
          <section>
            <h2 className="text-[10px] font-semibold uppercase tracking-widest text-gray-500 mb-2">
              Tools
            </h2>
            <div className="space-y-1.5">
              {TOOLS.map((item) => (
                <DisabledItem key={item.id} item={item} />
              ))}
            </div>
          </section>

          {/* Footer */}
          <div className="mt-auto pt-3 border-t border-gray-700 text-[10px] text-gray-500 leading-relaxed">
            <p>Phase 1 — GIS Foundation</p>
            <p className="text-gray-600">NER Landslide EWS v0.1.0</p>
          </div>
        </aside>

        {/* ── Map Area ────────────────────────────────────────────────── */}
        <main className="flex-1 relative overflow-hidden bg-gray-800">
          <MapView showHistoricalEvents={showHistoricalEvents} />
        </main>
      </div>
    </div>
  )
}
