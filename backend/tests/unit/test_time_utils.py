from datetime import timezone, timedelta
from app.utils.time_utils import utc_now, days_from_now, hours_from_now, is_expired


def test_utc_now_has_tz():
    assert utc_now().tzinfo is not None

def test_days_from_now():
    future = days_from_now(7)
    assert (future - utc_now()).days >= 6

def test_hours_from_now():
    future = hours_from_now(2)
    assert (future - utc_now()).total_seconds() >= 7000

def test_is_expired_past():
    past = utc_now() - timedelta(hours=1)
    assert is_expired(past) is True

def test_is_expired_future():
    future = utc_now() + timedelta(hours=1)
    assert is_expired(future) is False
