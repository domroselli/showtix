"""The current time in Las Vegas. Routes inject it so tests can pin the clock."""

from datetime import datetime
from zoneinfo import ZoneInfo

VEGAS = ZoneInfo("America/Los_Angeles")


def now() -> datetime:
    """Naive local Vegas time, matching how performance start times are stored."""
    return datetime.now(VEGAS).replace(tzinfo=None, microsecond=0)


def get_now() -> datetime:
    """FastAPI dependency for the current time. Tests override it to pin the clock."""
    return now()
