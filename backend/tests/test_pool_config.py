import pytest
from pydantic import ValidationError
from sqlalchemy.pool import AsyncAdaptedQueuePool


def test_default_pool_settings():
    from app.config import Settings

    s = Settings(SECRET_KEY="test")
    assert s.POOL_SIZE == 5
    assert s.MAX_OVERFLOW == 10
    assert s.POOL_RECYCLE == 3600


def test_custom_pool_settings():
    from app.config import Settings

    s = Settings(SECRET_KEY="test", POOL_SIZE=10, MAX_OVERFLOW=20, POOL_RECYCLE=1800)
    assert s.POOL_SIZE == 10
    assert s.MAX_OVERFLOW == 20
    assert s.POOL_RECYCLE == 1800


def test_pool_recycle_allows_minus_one():
    from app.config import Settings

    s = Settings(SECRET_KEY="test", POOL_RECYCLE=-1)
    assert s.POOL_RECYCLE == -1


def test_negative_pool_size_rejected():
    from app.config import Settings

    with pytest.raises(ValidationError):
        Settings(SECRET_KEY="test", POOL_SIZE=-1)


def test_negative_max_overflow_rejected():
    from app.config import Settings

    with pytest.raises(ValidationError):
        Settings(SECRET_KEY="test", MAX_OVERFLOW=-1)


def test_pool_recycle_below_minus_one_rejected():
    from app.config import Settings

    with pytest.raises(ValidationError):
        Settings(SECRET_KEY="test", POOL_RECYCLE=-2)


def test_engine_pool_params():
    from app.infrastructure.database import engine

    pool = engine.pool
    assert isinstance(pool, AsyncAdaptedQueuePool)
    assert pool.size() == 5
    assert pool._max_overflow == 10
    assert pool._recycle == 3600


def test_engine_pool_pre_ping():
    from app.infrastructure.database import engine

    assert engine.pool._pre_ping is True
