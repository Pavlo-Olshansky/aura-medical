# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Personal medical records tracker — FastAPI REST backend + Vue.js SPA frontend. PostgreSQL database. JWT authentication. All UI labels in Ukrainian. Timezone: `Europe/Kyiv`.

## Commands

```bash
# Backend
cd backend && source venv/bin/activate
uvicorn app.main:app --reload --port 8000   # Dev server (API docs at /docs)
pytest                                       # Run tests
alembic revision --autogenerate -m "msg"    # New migration
alembic upgrade head                         # Apply migrations

# Frontend
cd frontend
npm run dev      # Dev server (http://localhost:5173)
npm run build    # Production build
npm run lint     # Lint
```

## Architecture

- **`backend/`** — FastAPI application
  - `app/models/` — SQLAlchemy models (User, Visit, Treatment, Position, Procedure, Clinic, City)
  - `app/schemas/` — Pydantic v2 request/response schemas
  - `app/api/` — Route handlers (auth, visits, treatments, references, dashboard)
  - `app/auth/` — JWT token creation/verification, FastAPI dependencies
  - `app/services/` — Business logic (treatment status calculation)
  - `alembic/` — Database migrations
  - `scripts/` — Utility scripts
  - `tests/` — pytest tests
- **`frontend/`** — Vue.js 3 SPA with TypeScript
  - `src/views/` — Page components (Login, Dashboard, Visits, Treatments, References)
  - `src/components/` — Reusable components (AppLayout, DocumentPreview, StatusBadge)
  - `src/api/` — Axios API client with JWT interceptor
  - `src/stores/` — Pinia state management
  - `src/router/` — Vue Router with auth guard
- **`documents/`** — Uploaded medical files (production data; do not modify)
- Database: PostgreSQL (`medtracker`)

### Key Models (backend/app/models/)

- `BaseModel` — abstract base with `id`, `created`, `updated` timestamps
- `SoftDeleteModel` — extends BaseModel with `deleted_at` for soft delete
- `Visit` — central record: date, doctor, position, procedure, clinic, city, document path, link, comment
- `Treatment` — medication course with computed `status` property (active/completed based on date_start + days)
- `Position`, `Procedure`, `Clinic`, `City` — reference lookup tables
- `User` — single user with bcrypt-hashed password

### API Endpoints

- `POST /api/auth/login` — JWT login
- `GET /api/visits/` — paginated, filterable visit list
- `GET /api/treatments/` — treatment list with computed status
- `GET /api/{positions,procedures,clinics,cities}/` — reference data CRUD
- `GET /api/dashboard/` — overview with recent visits and active treatments

## Active Technologies
- Python 3.11+ (backend), TypeScript 5.x (frontend)
- FastAPI, SQLAlchemy 2.0+ (async), Pydantic v2, Alembic
- Vue.js 3, Vite, Vue Router, Pinia, PrimeVue, Axios
- PostgreSQL 15+
