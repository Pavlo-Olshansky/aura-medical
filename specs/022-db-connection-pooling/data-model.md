# Data Model: Database Connection Pooling

**Feature**: 022-db-connection-pooling | **Date**: 2026-04-10

## Overview

No new database models or schema changes. This feature only adds configuration fields to the existing Pydantic `Settings` class.

## Configuration Model Changes

### `Settings` (in `backend/app/config.py`)

New fields added to existing `Settings(BaseSettings)`:

| Field | Type | Default | Constraint | Env Var |
|-------|------|---------|------------|---------|
| `POOL_SIZE` | `int` | `5` | `>= 0` | `POOL_SIZE` |
| `MAX_OVERFLOW` | `int` | `10` | `>= 0` | `MAX_OVERFLOW` |
| `POOL_RECYCLE` | `int` | `3600` | `>= -1` | `POOL_RECYCLE` |

### Database Engine (in `backend/app/infrastructure/database.py`)

Parameters passed to `create_async_engine()`:

```python
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_size=settings.POOL_SIZE,
    max_overflow=settings.MAX_OVERFLOW,
    pool_recycle=settings.POOL_RECYCLE,
    pool_pre_ping=True,
)
```

## Schema Migrations

None required. No database tables affected.
