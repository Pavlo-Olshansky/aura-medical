# Research: Database Connection Pooling

**Feature**: 022-db-connection-pooling | **Date**: 2026-04-10

## Unknowns Identified

### 1. SQLAlchemy async pool class for psycopg_async

**Question**: Does `create_async_engine` with `postgresql+psycopg_async://` use `QueuePool` by default?

**Answer**: Yes. SQLAlchemy uses `QueuePool` as the default pool class for all non-SQLite, non-NullPool engines. The async variant (`AsyncAdaptedQueuePool`) wraps it transparently. No custom `poolclass` argument needed.

### 2. Supported pool parameters

**Question**: Which `create_async_engine` kwargs configure the pool?

**Answer**: The relevant kwargs are:
- `pool_size` (int, default 5) — number of persistent connections
- `max_overflow` (int, default 10) — extra connections above pool_size
- `pool_recycle` (int, default -1) — seconds before a connection is recycled; -1 = no recycle
- `pool_pre_ping` (bool, default False) — test connection liveness before checkout
- `pool_timeout` (int, default 30) — seconds to wait for available connection

Only `pool_size`, `max_overflow`, and `pool_recycle` are in scope per the spec. `pool_pre_ping=True` is a best practice for handling DB restarts but is not requested — can be added as a hardcoded `True` since it's purely beneficial with minimal overhead.

### 3. Pydantic-settings env var naming

**Question**: How will the settings fields map to env vars?

**Answer**: `pydantic-settings` auto-maps field names to uppercase env vars. Field `pool_size` → env var `POOL_SIZE`. No prefix needed since the project doesn't use `env_prefix`. This matches the existing pattern (e.g., `DATABASE_URL`, `SECRET_KEY`).

### 4. Impact on test suite

**Question**: Will explicit pool params break the test conftest?

**Answer**: No. The test conftest creates its own `test_engine = create_async_engine(TEST_DB_URL, echo=False)` independently. The production `engine` in `database.py` is only used in the app, which tests override via `dependency_overrides`. Pool settings on the production engine don't affect test behavior.

### 5. Validation approach

**Question**: How should invalid pool values be handled?

**Answer**: Pydantic v2 field validators with `ge=0` (for pool_size, max_overflow) and `ge=-1` (for pool_recycle, where -1 means no recycle). Invalid values will cause a startup crash via Pydantic's `ValidationError`, which is the correct behavior — fail fast with a clear error message rather than silently using bad values.

## Decisions

| # | Decision | Rationale |
|---|----------|-----------|
| 1 | Use Pydantic `Field(ge=...)` constraints, not custom validators | Simpler, declarative, built-in error messages |
| 2 | Add `pool_pre_ping=True` as hardcoded (not configurable) | Best practice for handling stale connections; no downside; always desirable |
| 3 | No new API endpoints | Security decision from clarification — pool stats not exposed |
| 4 | Test conftest unchanged | Test engine is independent; no pool params needed for test DB |
