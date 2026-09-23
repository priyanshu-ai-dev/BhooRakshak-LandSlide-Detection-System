# field-app/ — Field Reporting Application

**Status: Phase 0 — Not yet implemented.**

This module will contain a lightweight Progressive Web App (PWA) for field officers to:

- Submit GPS-tagged landslide observations with photos
- Mark high-risk road/infrastructure points
- Operate offline and sync when connectivity is restored

**Planned tech stack:** React PWA · Service Workers · IndexedDB (offline) · REST API → FastAPI backend

> Field reports are ingested via a dedicated `/api/v1/field-reports` endpoint added in a later phase.
