# Tasks: Database Connection Pooling

**Input**: Design documents from `/specs/022-db-connection-pooling/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to
- Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: No setup needed — project structure and dependencies already exist.

(No tasks — SQLAlchemy and pydantic-settings are already installed.)

---

## Phase 2: User Story 1 - Explicit Pool Configuration (Priority: P1) MVP

**Goal**: Add pool_size, max_overflow, pool_recycle as configurable settings and pass them to the async engine.

**Independent Test**: Start app with custom env vars, verify engine pool attributes match.

### Implementation

- [x] T001 [P] [US1] Add `POOL_SIZE`, `MAX_OVERFLOW`, `POOL_RECYCLE` fields with defaults and validators to `backend/app/config.py`
- [x] T002 [US1] Pass pool params + `pool_pre_ping=True` to `create_async_engine()` in `backend/app/infrastructure/database.py` (depends on T001)

### Tests

- [x] T003 [US1] Add `backend/tests/test_pool_config.py` — verify pool params are applied to the engine (depends on T002)

**Checkpoint**: Pool configuration is explicit, configurable via env vars, with defaults of pool_size=5, max_overflow=10, pool_recycle=3600.

---

## Phase 3: Polish

- [x] T004 Run full test suite (`pytest`) to verify no regressions (depends on T003)

---

## Dependencies & Execution Order

```
T001 ──→ T002 ──→ T003 ──→ T004
```

Strictly sequential — each task depends on the previous. No parallel opportunities (only 4 tasks, all touching related code).

### MVP Scope

T001–T003 deliver the full feature. T004 is validation only.

---

## Summary

| Metric | Value |
|--------|-------|
| Total tasks | 4 |
| User stories covered | 1 (US1 — only story in spec) |
| Parallel opportunities | 0 (sequential chain) |
| Files modified | 2 (`config.py`, `database.py`) |
| Files created | 1 (`test_pool_config.py`) |
| MVP tasks | T001–T003 |
