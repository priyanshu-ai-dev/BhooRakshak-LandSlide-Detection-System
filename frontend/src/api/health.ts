/**
 * api/health.ts — Client function for the health endpoint.
 *
 * Uses a relative URL so the Vite dev-server proxy transparently
 * forwards the request to the FastAPI backend.
 */
import { API_BASE_URL } from '../config'
import type { HealthResponse } from '../types/health'

export async function fetchHealth(): Promise<HealthResponse> {
  const url = `${API_BASE_URL}/api/v1/health`
  const response = await fetch(url)

  if (!response.ok) {
    throw new Error(
      `Health check failed — HTTP ${response.status} ${response.statusText}`,
    )
  }

  return response.json() as Promise<HealthResponse>
}
