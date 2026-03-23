from __future__ import annotations
from datetime import datetime, timezone, timedelta


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def days_from_now(days: int) -> datetime:
    return utc_now() + timedelta(days=days)


def hours_from_now(hours: int) -> datetime:
    return utc_now() + timedelta(hours=hours)


def is_expired(dt: datetime) -> bool:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt < utc_now()


def format_date(dt: datetime) -> str:
    return dt.strftime("%b %d, %Y")


def format_datetime(dt: datetime) -> str:
    return dt.strftime("%b %d, %Y %I:%M %p")
