# Backward-compat re-export — new code should use app.api.dependencies.get_current_user
from app.api.dependencies import get_current_user  # noqa: F401
