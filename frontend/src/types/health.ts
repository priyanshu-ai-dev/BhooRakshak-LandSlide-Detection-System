/**
 * types/health.ts — Type definitions for the health API response.
 * Must stay in sync with backend/app/api/v1/endpoints/health.py :: HealthResponse
 */
export interface HealthResponse {
  status: string
  version: string
  service: string
  phase: string
}
