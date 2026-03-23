"""Tests for order number generation."""
from app.utils.order_number import generate_order_number, generate_tracking_number, generate_payout_reference


def test_order_number_format():
    num = generate_order_number()
    assert num.startswith("ORD-")
    parts = num.split("-")
    assert len(parts) == 3
    assert len(parts[1]) == 8  # YYYYMMDD
    assert len(parts[2]) == 4  # random

def test_order_numbers_unique():
    nums = {generate_order_number() for _ in range(100)}
    assert len(nums) == 100

def test_tracking_number_prefix():
    assert generate_tracking_number("fedex").startswith("FDX")
    assert generate_tracking_number("ups").startswith("UPS")
    assert generate_tracking_number("internal").startswith("BZR")

def test_payout_reference_format():
    ref = generate_payout_reference()
    assert ref.startswith("PAY-")
