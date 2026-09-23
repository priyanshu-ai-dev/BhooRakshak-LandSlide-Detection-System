# NER Landslide Early Warning System (EWS)

> AI-based Landslide Early Warning and Risk Monitoring System for Northeast India.  
> **Current status: Phase 1 — GIS Foundation**

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Repository Structure](#repository-structure)
3. [Quick Start](#quick-start)
4. [Running Each Service](#running-each-service)
5. [Environment Variables](#environment-variables)
6. [API Reference](#api-reference)
7. [Phase Roadmap](#phase-roadmap)

---

## Prerequisites

| Tool | Minimum Version | Purpose |
|---|---|---|
| [Docker Desktop](https://www.docker.com/products/docker-desktop/) | 24+ | PostgreSQL/PostGIS container |
| [Python](https://python.org) | 3.11 | Backend (FastAPI) & Ingestion scripts |
| [Node.js](https://nodejs.org) | 18+ | Frontend (Vite/React) |
| [npm](https://npmjs.com) | 9+ | Frontend package manager |

---

## Repository Structure

```
ner-landslide-ews/
├── frontend/          # React + Vite + TypeScript + MapLibre GL
├── backend/           # FastAPI + SQLAlchemy + GeoAlchemy2
├── ml/                # ML pipelines (Phase 3+)
├── ingestion/         # Data ingestion pipelines (Phase 1+)
├── field-app/         # Field officer PWA (Phase 2+)
├── database/
│   └── init/          # SQL scripts auto-run by PostGIS on first boot
├── docs/              # Architecture & API documentation
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## Quick Start

### 1. Clone & configure environment

```bash
git clone <repo-url>
cd ner-landslide-ews

# Copy the environment template and fill in your values
copy .env.example .env    # Windows
# cp .env.example .env    # macOS / Linux
```

> **Minimum required change:** Update `POSTGRES_PASSWORD` in `.env` before running.

### 2. Start PostgreSQL + PostGIS

```bash
docker compose up db -d
```

Wait for the health check to pass (≈15 seconds):

```bash
docker compose ps   # db should show "healthy"
```

### 3. Load GIS Data (Phase 1)
Follow the [Phase 1 GIS Layer Documentation](docs/phase1_gis_layer.md) to download the NASA GLC dataset and run the ingest script:
```bash
pip install -r ingestion/requirements.txt
python ingestion/import_nasa_glc.py
```

### 4. Start the Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Verify: `http://localhost:8000/api/v1/health` should return HTTP 200.

### 5. Start the Frontend

Open a new terminal:

```bash
cd frontend
npm install
npm run dev
```

Open: **http://localhost:5173**

---

## Running Each Service

### PostgreSQL / PostGIS only

```bash
docker compose up db -d
docker compose logs -f db       # tail logs
docker compose stop db          # stop without deleting data
docker compose down             # stop and remove containers
docker compose down -v          # ⚠️  also deletes the postgres_data volume
```

### Full stack via Docker Compose (optional)

```bash
docker compose --profile full up --build
```

This starts `db`, `backend`, and `frontend` together. The backend and frontend containers are in the `full` profile to keep `docker compose up db` lightweight during development.

### Backend (manual — recommended during development)

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Interactive API docs: http://localhost:8000/docs

### Frontend (manual — recommended during development)

```bash
cd frontend
npm run dev          # start dev server with HMR
npm run build        # type-check + production build
npm run typecheck    # TypeScript check only
```

---

## Environment Variables

Copy `.env.example` → `.env` and configure:

| Variable | Default | Description |
|---|---|---|
| `POSTGRES_DB` | `ner_landslide` | Database name |
| `POSTGRES_USER` | `postgres` | DB superuser |
| `POSTGRES_PASSWORD` | _(must set)_ | DB password |
| `POSTGRES_PORT` | `5432` | Published host port |
| `DATABASE_URL` | `postgresql://...` | Full SQLAlchemy URL for the backend |
| `BACKEND_PORT` | `8000` | Backend HTTP port |
| `DEBUG` | `false` | Enable SQLAlchemy SQL echo |
| `CORS_ORIGINS` | `http://localhost:5173,...` | Comma-separated CORS allow-list |
| `VITE_API_BASE_URL` | _(empty)_ | Leave empty for dev (Vite proxy used) |

---

## API Reference

| Method | Path | Description |
|---|---|---|
| `GET` | `/` | Service info + navigation links |
| `GET` | `/api/v1/health` | Backend health status |
| `GET` | `/api/v1/gis/layers` | List available GIS layers |
| `GET` | `/api/v1/gis/layers/{layer_id}` | GeoJSON FeatureCollection for a layer |
| `GET` | `/docs` | Swagger UI |
| `GET` | `/redoc` | ReDoc UI |

---

## Phase Roadmap

| Phase | Description | Status |
|---|---|---|
| **0** | Repository scaffold, PostGIS, FastAPI shell, MapLibre map | ✅ Complete |
| **1** | GIS foundation, NASA GLC historical event inventory layer | ✅ Complete |
| **2** | Live rainfall/soil-moisture ingestion, field reporting API | 🔜 Next |
| **3** | ML susceptibility model (XGBoost + SHAP), risk scoring | Planned |
| **4** | Alert delivery (email / SMS / webhook) | Planned |
| **5** | Authentication, RBAC, production hardening | Planned |

