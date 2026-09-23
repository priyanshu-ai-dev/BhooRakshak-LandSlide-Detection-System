import React from 'react'

/**
 * SusceptibilityLegend — Displays color mapping for the historical landslide events layer.
 */
export default function SusceptibilityLegend() {
  return (
    <div className="absolute bottom-8 right-3 z-10 bg-gray-900/90 backdrop-blur-md p-3 rounded-lg border border-gray-700 shadow-xl text-xs w-64 pointer-events-auto">
      <h3 className="font-semibold text-gray-200 mb-1">Historical Landslide Events</h3>
      <p className="text-gray-400 mb-3 text-[10px] leading-tight">
        Reported incidents from the NASA Global Landslide Catalog. Not a live warning system.
      </p>
      
      <div className="space-y-2">
        <div className="flex items-center gap-2">
          <span className="w-3 h-3 rounded-full bg-[#dc2626] border border-white/20 shrink-0" />
          <span className="text-gray-300">Catastrophic</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-3 h-3 rounded-full bg-[#ea580c] border border-white/20 shrink-0" />
          <span className="text-gray-300">Very Large</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-3 h-3 rounded-full bg-[#d97706] border border-white/20 shrink-0" />
          <span className="text-gray-300">Large</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-3 h-3 rounded-full bg-[#65a30d] border border-white/20 shrink-0" />
          <span className="text-gray-300">Medium</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-3 h-3 rounded-full bg-[#6b7280] border border-white/20 shrink-0" />
          <span className="text-gray-300">Small / Unknown</span>
        </div>
      </div>
    </div>
  )
}
