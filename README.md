# MedTracker

Personal medical records tracker with an interactive body map, visit history, treatment monitoring, and document management. Built with FastAPI and Vue.js. All UI labels in Ukrainian.

## Demo

![MedTracker Demo](medical.gif)


## Features

- **Interactive Body Map** — sex-aware anatomical visualization (front, back, face) with 50+ clickable hotspots mapped to body regions. Highlights areas with active treatments, supports click-to-filter visits by region
- **Visit Records** — track doctor visits with date, specialty, procedure, clinic, city, body region, comments, and attached documents
- **Treatment Tracking** — medication courses with automatic status calculation (active/completed) based on start date and duration
- **Dashboard** — summary cards, recent visits, active treatments, and body map overview at a glance
- **Health Profile** — demographics, blood type, allergies, chronic conditions, emergency contact
- **Document Management** — upload and preview medical documents (images, PDFs) attached to visits
- **Reference Data** — manage doctor specialties, procedures, clinics, and cities with inline CRUD
- **Filtering & Search** — visits filterable by date range, clinic, city, procedure, doctor specialty; treatments by status

## Tech Stack

| Layer | Technologies |
|-------|-------------|
| **Frontend** | Vue.js 3, TypeScript, PrimeVue, Pinia, Vue Router, Vite |
| **Backend** | FastAPI, SQLAlchemy 2.0 (async), Pydantic v2, Alembic |
| **Database** | PostgreSQL 15+ |
| **Auth** | JWT tokens, bcrypt password hashing |

## Architecture

```
backend/
  app/
    api/            # Route handlers (auth, visits, treatments, references, dashboard, profile)
    domain/         # Domain models and business logic
    infrastructure/ # Database engine, session management
    models/         # SQLAlchemy ORM models
    schemas/        # Pydantic request/response schemas
    services/       # Application services
  alembic/          # Database migrations
  tests/            # pytest test suite

frontend/
  src/
    views/          # Page components (Dashboard, Visits, Treatments, References, Profile)
    components/     # Reusable UI (BodyMap, AppLayout, DocumentPreview, StatusBadge)
    api/            # Axios client with JWT interceptor
    stores/         # Pinia state management
    router/         # Vue Router with auth guards
```

## Getting Started

**Prerequisites:** Python 3.11+, Node.js 20+, PostgreSQL 15+

```bash
# Clone and install
git clone
make install

# Create database and run migrations
make db-create
make db-migrate

# Start development servers
make dev
```

Backend runs at `http://localhost:8000` (API docs at `/docs`), frontend at `http://localhost:5173`.

## Available Commands

```bash
make dev              # Start backend + frontend
make backend          # Start backend only
make frontend         # Start frontend only
make test             # Run tests
make lint             # Lint frontend
make build            # Production frontend build
make db-migrate       # Run Alembic migrations
make db-revision msg="description"  # Generate new migration
make backup           # Backup PostgreSQL database
```

## License

This is a personal project actively used. The source code is shared for portfolio and reference purposes. All rights reserved.
