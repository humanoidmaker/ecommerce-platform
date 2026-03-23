"""Tests for shipping calculator."""
from decimal import Decimal
from app.services.shipping_calculator import calculate_shipping, get_all_shipping_options, estimate_delivery_date


def test_standard_base_price():
    result = calculate_shipping("standard", Decimal("1.0"), Decimal("50.00"))
    assert result["cost"] == Decimal("6.49")  # 5.99 + 0.50*1
    assert result["method"] == "standard"

def test_express_with_weight():
    result = calculate_shipping("express", Decimal("3.0"), Decimal("50.00"))
    assert result["cost"] == Decimal("15.99")  # 12.99 + 1.00*3

def test_overnight_pricing():
    result = calculate_shipping("overnight", Decimal("2.0"), Decimal("50.00"))
    assert result["cost"] == Decimal("28.99")  # 24.99 + 2.00*2

def test_free_shipping_threshold():
    result = calculate_shipping("standard", Decimal("1.0"), Decimal("100.00"))
    assert result["cost"] == Decimal("0.00")
    assert result["free_shipping"] is True

def test_free_shipping_only_standard():
    result = calculate_shipping("express", Decimal("1.0"), Decimal("100.00"))
    assert result["cost"] > Decimal("0.00")
    assert result["free_shipping"] is False

def test_zero_weight_uses_minimum():
    result = calculate_shipping("standard", Decimal("0"), Decimal("50.00"))
    assert result["cost"] == Decimal("6.04")  # 5.99 + 0.50*0.1

def test_all_shipping_options():
    options = get_all_shipping_options(Decimal("1.0"), Decimal("50.00"))
    assert len(options) == 3
    methods = {o["method"] for o in options}
    assert methods == {"standard", "express", "overnight"}

def test_delivery_estimate():
    est = estimate_delivery_date("standard")
    assert est["earliest"] is not None
    assert est["latest"] is not None

def test_invalid_method_raises():
    import pytest
    with pytest.raises(ValueError):
        calculate_shipping("teleport", Decimal("1.0"), Decimal("50.00"))
