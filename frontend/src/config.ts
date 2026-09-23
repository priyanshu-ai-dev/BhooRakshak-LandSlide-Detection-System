/**
 * config.ts — Centralised runtime configuration.
 *
 * VITE_API_BASE_URL should be empty string in local development so that
 * relative /api/* requests are handled by the Vite dev-server proxy.
 * In production, set it to the full backend URL, e.g. https://api.example.com
 */
export const API_BASE_URL: string = import.meta.env.VITE_API_BASE_URL ?? ''
