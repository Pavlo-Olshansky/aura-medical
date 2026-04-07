.PHONY: help backend frontend dev test test-backend lint build db-create db-migrate db-revision seed docker-up docker-down docker-seed docker-logs backup install

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

# --- Development ---

backend: ## Start backend dev server (port 8000)
	cd backend && source venv3.14/bin/activate && uvicorn app.main:app --reload --port 8000

frontend: ## Start frontend dev server (port 5173)
	cd frontend && npm run dev

dev: ## Start both backend and frontend
	@echo "Starting backend and frontend..."
	$(MAKE) backend &
	$(MAKE) frontend

dev-pwa: ## Start backend + production frontend build (for testing push notifications)
	@echo "Building frontend and starting PWA mode..."
	cd frontend && npm run build
	$(MAKE) backend &
	cd frontend && npx serve dist -l 5173

# --- Testing ---

test: test-backend ## Run all tests

test-backend: ## Run backend tests
	cd backend && source venv3.14/bin/activate && pytest tests/ -v

# --- Build & Lint ---

build: ## Build frontend for production
	cd frontend && npm run build

lint: ## Lint frontend code
	cd frontend && npm run lint

# --- Database ---

db-create: ## Create PostgreSQL database
	createdb medtracker

db-migrate: ## Run Alembic migrations
	cd backend && source venv3.14/bin/activate && alembic upgrade head

db-revision: ## Generate new Alembic migration (usage: make db-revision msg="add column")
	cd backend && source venv3.14/bin/activate && alembic revision --autogenerate -m "$(msg)"

seed: ## Create default admin/admin user
	cd backend && python -m scripts.create_user admin admin

# --- Docker ---

docker-up: ## Start dev environment with Docker Compose
	docker compose up --build -d

docker-down: ## Stop Docker Compose services
	docker compose down

docker-seed: ## Create admin user in Docker backend
	docker compose exec backend python -m scripts.create_user admin admin

docker-logs: ## Tail Docker Compose logs
	docker compose logs -f

backup: ## Backup PostgreSQL database to backups/
	@mkdir -p backups
	pg_dump -Fc medtracker -f backups/medtracker_$$(date +%Y%m%d_%H%M%S).dump
	@echo "Backup saved to backups/"
	# Restore: pg_restore -d medtracker --clean --if-exists backups/<filename>.dump

# --- Setup ---

install: install-backend install-frontend ## Install all dependencies

install-backend: ## Install backend dependencies
	cd backend && python3.14 -m venv venv3.14 && source venv3.14/bin/activate && pip install -r requirements.txt

install-frontend: ## Install frontend dependencies
	cd frontend && npm install
