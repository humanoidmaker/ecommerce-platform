"""Generate human-readable order numbers: ORD-YYYYMMDD-XXXX."""
from __future__ import annotations
import random
import string
from datetime import datetime, timezone


def generate_order_number() -> str:
    """Generate a unique order number: ORD-YYYYMMDD-XXXX."""
    now = datetime.now(timezone.utc)
    date_part = now.strftime("%Y%m%d")
    random_part = "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"ORD-{date_part}-{random_part}"


def generate_tracking_number(carrier: str = "internal") -> str:
    """Generate a mock tracking number."""
    prefix = {"internal": "BZR", "fedex": "FDX", "ups": "UPS", "dhl": "DHL", "usps": "USPS"}.get(carrier, "TRK")
    num = "".join(random.choices(string.digits, k=12))
    return f"{prefix}{num}"


def generate_payout_reference() -> str:
    """Generate payout reference: PAY-YYYYMMDD-XXXX."""
    now = datetime.now(timezone.utc)
    date_part = now.strftime("%Y%m%d")
    random_part = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"PAY-{date_part}-{random_part}"
