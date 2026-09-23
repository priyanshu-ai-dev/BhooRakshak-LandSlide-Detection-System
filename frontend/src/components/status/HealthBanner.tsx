import { useEffect, useState } from 'react'
import { fetchHealth } from '../../api/health'
import type { HealthResponse } from '../../types/health'

type LoadState = 'loading' | 'ok' | 'error'

/**
 * HealthBanner — displays the live backend connectivity status in the nav bar.
 *
 * States:
 *  loading → pulsing yellow dot while the fetch is in flight
 *  ok      → green dot with version info
 *  error   → red dot with a tooltip containing the error message
 */
export default function HealthBanner() {
  const [loadState, setLoadState] = useState<LoadState>('loading')
  const [data, setData] = useState<HealthResponse | null>(null)
  const [errorDetail, setErrorDetail] = useState<string>('')

  useEffect(() => {
    let cancelled = false

    fetchHealth()
      .then((res) => {
        if (!cancelled) {
          setData(res)
          setLoadState('ok')
        }
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          setErrorDetail(err instanceof Error ? err.message : String(err))
          setLoadState('error')
        }
      })

    return () => {
      cancelled = true
    }
  }, [])

  if (loadState === 'loading') {
    return (
      <div className="flex items-center gap-2 text-sm text-gray-400">
        <span className="w-2 h-2 rounded-full bg-yellow-400 animate-pulse" />
        Checking backend…
      </div>
    )
  }

  if (loadState === 'error') {
    return (
      <div
        className="flex items-center gap-2 text-sm text-red-400 cursor-help"
        title={errorDetail}
      >
        <span className="w-2 h-2 rounded-full bg-red-500" />
        Backend: Unreachable
      </div>
    )
  }

  return (
    <div className="flex items-center gap-2 text-sm text-green-400">
      <span className="w-2 h-2 rounded-full bg-green-400" />
      <span>
        Backend: <strong>{data?.status?.toUpperCase()}</strong>
      </span>
      <span className="text-gray-500">·</span>
      <span className="text-gray-400">v{data?.version}</span>
      <span className="text-gray-500">·</span>
      <span className="text-gray-500 text-xs">Phase {data?.phase}</span>
    </div>
  )
}
