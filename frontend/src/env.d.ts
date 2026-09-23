/// <reference types="vite/client" />

/**
 * Augment ImportMetaEnv with project-specific variables.
 * Any variable added to .env.example must also be declared here.
 */
interface ImportMetaEnv {
  /** Backend base URL. Leave empty in dev — Vite proxy handles /api/* */
  readonly VITE_API_BASE_URL: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
