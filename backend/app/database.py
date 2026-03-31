# Backward-compat re-export — all code should migrate to app.infrastructure.database
from app.infrastructure.database import engine, async_session, get_session  # noqa: F401
