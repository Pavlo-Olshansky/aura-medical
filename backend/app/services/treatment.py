from datetime import datetime, timedelta

try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo

KYIV_TZ = ZoneInfo("Europe/Kyiv")


def compute_status(date_start: datetime, days: int) -> str:
    """Return 'active' if treatment end date is in the future, else 'completed'."""
    now = datetime.now(KYIV_TZ)
    end_date = date_start + timedelta(days=days)
    if end_date.tzinfo is None:
        end_date = end_date.replace(tzinfo=KYIV_TZ)
    return "active" if end_date > now else "completed"
