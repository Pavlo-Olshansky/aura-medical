# MedTracker

Personal medical records tracker with an interactive body map, visit history, treatment monitoring, and document management. Built with FastAPI and Vue.js. All UI labels in Ukrainian.

## Demo

<video src="medical.mp4" autoplay loop muted playsinline width="100%"></video>


## Features

- **Interactive Body Map** — sex-aware anatomical visualization (front, back, face) with 50+ clickable hotspots mapped to body regions. Highlights areas with active treatments, supports click-to-filter visits by region
- **Visit Records** — track doctor visits with date, specialty, procedure, clinic, city, body region, comments, and attached documents
- **Treatment Tracking** — medication courses with automatic status calculation (active/completed) based on start date and duration
- **Lab Results & Biomarker Trends** — blood tests with reference ranges, out-of-range highlighting, and trend charts per biomarker over time
- **Health Metrics / Vitals Journal** — track heart rate, blood pressure, temperature, weight and other metrics with trend charts and reference range annotations
- **Vaccination Records** — immunization history with dose tracking, next-due-date alerts, and document attachments
- **Medical Timeline** — unified chronological view of all events (visits, treatments, lab results, vaccinations) across the full health history
- **Dashboard** — summary cards, recent visits, active treatments, expenses, and body map overview at a glance
- **Health Profile** — demographics, blood type, allergies, chronic conditions, emergency contact
- **Document Management** — upload and preview medical documents (images, PDFs) attached to visits and vaccinations
- **Reference Data** — manage doctor specialties, procedures, clinics, cities, biomarker references, and metric types with inline CRUD
- **Filtering & Search** — visits filterable by date range, clinic, city, procedure, doctor specialty; treatments by status

## Tech Stack

| Layer | Technologies |
|-------|-------------|
| **Frontend** | Vue.js 3, TypeScript, PrimeVue, Pinia, Vue Router, Vite, Chart.js |
| **Backend** | Python 3.14+, FastAPI, SQLAlchemy 2.0 (async), Pydantic v2, Alembic |
| **Database** | PostgreSQL 15+ |
| **Auth** | JWT tokens (PyJWT), bcrypt password hashing |
| **DB Driver** | psycopg v3 (async) |

## Architecture

```
backend/
  app/
    api/              # Route handlers (auth, visits, treatments, lab results, health metrics, etc.)
    application/      # Application services and commands
    domain/           # Domain entities, value objects, repository interfaces, exceptions
    infrastructure/   # Database engine, ORM models, repository implementations, JWT
      models/         # SQLAlchemy ORM models
      repositories/   # Repository implementations
    schemas/          # Pydantic request/response schemas
  alembic/            # Database migrations
  tests/              # pytest test suite

frontend/
  src/
    views/            # Page components (Dashboard, Visits, Treatments, Lab Results, Timeline, etc.)
    components/       # Reusable UI (BodyMap, Charts, AppLayout, DocumentPreview)
    api/              # Axios client with JWT interceptor
    stores/           # Pinia state management
    router/           # Vue Router with auth guards
    types/            # TypeScript interfaces and payload types
    utils/            # Shared utilities (date formatting, chart setup)
```

## Getting Started

**Prerequisites:** Python 3.14+, Node.js 20+, PostgreSQL 15+

```bash
# Clone and install
git clone
make install

# Configure environment
cp backend/.env.example backend/.env
# Edit backend/.env — set SECRET_KEY (required) and other settings

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
