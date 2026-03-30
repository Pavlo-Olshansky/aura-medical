.PHONY: help backend frontend dev test test-backend lint build migrate db-create db-migrate backup

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

# --- Development ---

backend: ## Start backend dev server (port 8000)
	cd backend && source venv/bin/activate && uvicorn app.main:app --reload --port 8000

frontend: ## Start frontend dev server (port 5173)
	cd frontend && npm run dev

dev: ## Start both backend and frontend
	@echo "Starting backend and frontend..."
	$(MAKE) backend &
	$(MAKE) frontend

# --- Testing ---

test: test-backend ## Run all tests

test-backend: ## Run backend tests
	cd backend && source venv/bin/activate && pytest tests/ -v

# --- Build & Lint ---

build: ## Build frontend for production
	cd frontend && npm run build

lint: ## Lint frontend code
	cd frontend && npm run lint

# --- Database ---

db-create: ## Create PostgreSQL database
	createdb medtracker

db-migrate: ## Run Alembic migrations
	cd backend && source venv/bin/activate && alembic upgrade head

db-revision: ## Generate new Alembic migration (usage: make db-revision msg="add column")
	cd backend && source venv/bin/activate && alembic revision --autogenerate -m "$(msg)"

# --- Data Migration ---

backup: ## Backup SQLite database and documents
	mkdir -p backups
	cp db.sqlite3 backups/db.sqlite3.bak
	cp -r documents backups/documents

migrate-data: ## One-time SQLite to PostgreSQL migration (set PG_URL)
	cd backend && source venv/bin/activate && python scripts/migrate_from_sqlite.py \
		--sqlite ../db.sqlite3 \
		--pg $(or $(PG_URL),postgresql://postgres:postgres@localhost:5432/medtracker)

# --- Setup ---

install: install-backend install-frontend ## Install all dependencies

install-backend: ## Install backend dependencies
	cd backend && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt

install-frontend: ## Install frontend dependencies
	cd frontend && npm install
