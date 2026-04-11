# Implementation Plan: Database Connection Pooling

**Branch**: `022-db-connection-pooling` | **Date**: 2026-04-10 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/022-db-connection-pooling/spec.md`

## Summary

Configure SQLAlchemy's async engine with explicit connection pool parameters (`pool_size`, `max_overflow`, `pool_recycle`) via Pydantic settings, replacing implicit SQLAlchemy defaults. No new endpoints — configuration only.

## Technical Context

**Language/Version**: Python 3.14+ (backend only)
**Primary Dependencies**: FastAPI, SQLAlchemy 2.0+ (async), Pydantic v2, pydantic-settings
**Storage**: PostgreSQL via `psycopg_async` driver
**Testing**: pytest + pytest-asyncio
**Target Platform**: Linux server / macOS dev
**Project Type**: web-service (backend only — no frontend changes)
**Performance Goals**: N/A (configuration feature, no new runtime paths)
**Constraints**: Must not break existing tests; pool params must be env-configurable
**Scale/Scope**: 2 files modified, 1 test file added

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. FastAPI + Vue.js Architecture | PASS | Backend-only change within FastAPI layer |
| II. Data Integrity First | PASS | No schema changes; pool config doesn't affect data integrity |
| III. Privacy & Security | PASS | No new endpoints; pool metrics explicitly excluded (security decision) |
| IV. Test Coverage | PASS | Tests planned for pool configuration verification |
| V. Simplicity & Incremental Growth | PASS | Minimal change: 3 settings fields + engine params |
| VI. Ukrainian-First UI | N/A | No UI changes |
| VII. Modular Domain Design | PASS | Changes are in infrastructure layer where they belong |

No violations. Gate passed.

## Project Structure

### Documentation (this feature)

```text
specs/022-db-connection-pooling/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output (minimal — no new models)
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (empty — no new API contracts)
└── tasks.md             # Phase 2 output
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── config.py                    # ADD: pool_size, max_overflow, pool_recycle fields
│   └── infrastructure/
│       └── database.py              # MODIFY: pass pool params to create_async_engine
└── tests/
    └── test_pool_config.py          # ADD: verify pool params applied correctly
```

**Structure Decision**: Backend-only, infrastructure layer. Two existing files modified (`config.py`, `database.py`), one new test file.

## Complexity Tracking

No violations — table not needed.
