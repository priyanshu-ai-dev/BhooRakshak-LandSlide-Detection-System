import MapView from '../map/MapView'
import HealthBanner from '../status/HealthBanner'

/** Sidebar layer/tool entry (disabled in Phase 0) */
interface SidebarItem {
  label: string
  availableFrom: string
}

const RISK_LAYERS: SidebarItem[] = [
  { label: 'Susceptibility', availableFrom: 'Phase 1' },
  { label: 'Rainfall', availableFrom: 'Phase 1' },
  { label: 'Soil Moisture', availableFrom: 'Phase 1' },
  { label: 'Seismic Activity', availableFrom: 'Phase 1' },
]

const TOOLS: SidebarItem[] = [
  { label: 'Field Reports', availableFrom: 'Phase 2' },
  { label: 'Alert Log', availableFrom: 'Phase 2' },
  { label: 'ML Inference', availableFrom: 'Phase 3' },
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
          {/* Risk Layers */}
          <section>
            <h2 className="text-[10px] font-semibold uppercase tracking-widest text-gray-500 mb-2">
              Risk Layers
            </h2>
            <div className="space-y-1.5">
              {RISK_LAYERS.map((item) => (
                <DisabledItem key={item.label} item={item} />
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
                <DisabledItem key={item.label} item={item} />
              ))}
            </div>
          </section>

          {/* Footer */}
          <div className="mt-auto pt-3 border-t border-gray-700 text-[10px] text-gray-600 leading-relaxed">
            <p>Phase 0 — Infrastructure Shell</p>
            <p className="text-gray-700">NER Landslide EWS v0.1.0</p>
          </div>
        </aside>

        {/* ── Map Area ────────────────────────────────────────────────── */}
        <main className="flex-1 relative overflow-hidden">
          <MapView />
        </main>
      </div>
    </div>
  )
}
