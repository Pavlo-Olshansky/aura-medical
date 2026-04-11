# Feature Specification: Database Connection Pooling

**Feature Branch**: `022-db-connection-pooling`
**Created**: 2026-04-10
**Status**: Draft
**Input**: User description: "Database Connection Pooling — Configure SQLAlchemy async pool explicitly: pool_size, max_overflow, pool_recycle. Add connection pool monitoring metrics. Currently uses defaults."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Explicit Pool Configuration (Priority: P1)

As a developer/operator, I want the SQLAlchemy async engine to use explicitly configured pool parameters (`pool_size`, `max_overflow`, `pool_recycle`) so that database connection behavior is predictable and tunable per environment rather than relying on library defaults.

**Why this priority**: Without explicit pool settings, the application relies on SQLAlchemy defaults which may not match production workload requirements. This is the core ask.

**Independent Test**: Can be verified by checking the engine's pool attributes after initialization and confirming they match configured values.

**Acceptance Scenarios**:

1. **Given** the application starts with pool settings in environment/config, **When** the async engine is created, **Then** the engine pool has `pool_size`, `max_overflow`, and `pool_recycle` matching the configured values.
2. **Given** no pool environment variables are set, **When** the application starts, **Then** the defaults `pool_size=5, max_overflow=10, pool_recycle=3600` are used.

---

### Edge Cases

- How does pool behave after a database restart? (`pool_recycle` should handle stale connections)
- What if invalid pool configuration values are provided (e.g., negative pool_size)?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow `pool_size`, `max_overflow`, and `pool_recycle` to be configured via environment variables or application settings.
- **FR-002**: System MUST apply configured pool parameters to the `create_async_engine` call in `backend/app/infrastructure/database.py`.
- **FR-003**: System MUST provide configurable default values: `pool_size=5`, `max_overflow=10`, `pool_recycle=3600` (seconds). These defaults apply when the corresponding environment variables are not set.
- **FR-004**: System MUST validate pool configuration values at startup (non-negative integers, pool_recycle in seconds).

### Key Entities

- **Pool Configuration**: Settings object fields for `pool_size` (int), `max_overflow` (int), `pool_recycle` (int, seconds).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Pool parameters are explicitly set on the async engine (verified via `engine.pool.size()`, `engine.pool.overflow()`, etc.)
- **SC-002**: All existing tests continue to pass with the new pool configuration.
- **SC-004**: Configuration can be changed via environment variables without code changes.

## Clarifications

### Session 2026-04-10

- Q: What default pool parameter values when not set via env vars? → A: `pool_size=5, max_overflow=10, pool_recycle=3600` — configurable defaults, overridable per environment.
- Q: Should pool metrics endpoint require JWT auth? → A: Skip pool metrics endpoint entirely — only configure the pool, no monitoring API. Avoids exposing infrastructure details.

## Assumptions

- The existing `psycopg_async` driver supports SQLAlchemy's `QueuePool` (default async pool class) — no custom pool class needed.
- This is a single-instance application; no cross-process pool coordination is required.
- The existing health endpoints at `/health` and `/health/ready` remain unchanged.
- Pool monitoring metrics endpoint is explicitly out of scope (security concern — avoids exposing infrastructure details).
