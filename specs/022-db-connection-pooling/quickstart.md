# Quickstart: Database Connection Pooling

**Feature**: 022-db-connection-pooling | **Date**: 2026-04-10

## What Changed

Explicit connection pool parameters added to the SQLAlchemy async engine configuration.

## Configuration

Set via environment variables or `.env` file:

```env
# Connection pool settings (all optional — defaults shown)
POOL_SIZE=5          # Persistent connections in the pool
MAX_OVERFLOW=10      # Extra connections above pool_size
POOL_RECYCLE=3600    # Recycle connections after N seconds (-1 = never)
```

## Verification

```bash
cd backend && source venv/bin/activate

# Run tests
pytest tests/test_pool_config.py -v

# Run all tests to verify no regressions
pytest
```

## Files Modified

| File | Change |
|------|--------|
| `backend/app/config.py` | Added `POOL_SIZE`, `MAX_OVERFLOW`, `POOL_RECYCLE` fields |
| `backend/app/infrastructure/database.py` | Pass pool params + `pool_pre_ping=True` to engine |
| `backend/tests/test_pool_config.py` | New test file for pool configuration |
