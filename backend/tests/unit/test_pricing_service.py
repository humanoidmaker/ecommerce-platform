"""Tests for pricing service — ALL Decimal, critical money path."""
from decimal import Decimal
from app.services.pricing_service import get_item_price, calc_line_total, apply_coupon, calc_cart_totals


def test_item_price_no_variant():
    assert get_item_price(Decimal("29.99")) == Decimal("29.99")

def test_item_price_with_variant_override():
    assert get_item_price(Decimal("29.99"), Decimal("34.99")) == Decimal("34.99")

def test_item_price_variant_none_uses_product():
    assert get_item_price(Decimal("29.99"), None) == Decimal("29.99")

def test_line_total():
    assert calc_line_total(Decimal("10.00"), 3) == Decimal("30.00")

def test_percentage_coupon():
    assert apply_coupon(Decimal("100.00"), "percentage", Decimal("20")) == Decimal("20.00")

def test_fixed_coupon():
    assert apply_coupon(Decimal("100.00"), "fixed_amount", Decimal("15.00")) == Decimal("15.00")

def test_fixed_coupon_exceeds_subtotal():
    assert apply_coupon(Decimal("10.00"), "fixed_amount", Decimal("15.00")) == Decimal("10.00")

def test_free_shipping_coupon_returns_zero():
    assert apply_coupon(Decimal("100.00"), "free_shipping", Decimal("0")) == Decimal("0.00")

def test_min_order_not_met():
    assert apply_coupon(Decimal("20.00"), "percentage", Decimal("10"), min_order=Decimal("50.00")) == Decimal("0.00")

def test_max_discount_cap():
    assert apply_coupon(Decimal("1000.00"), "percentage", Decimal("50"), max_discount=Decimal("100.00")) == Decimal("100.00")

def test_cart_totals_basic():
    items = [{"unit_price": Decimal("25.00"), "quantity": 2, "tax_rate": Decimal("0.08")}]
    totals = calc_cart_totals(items)
    assert totals["subtotal"] == Decimal("50.00")
    assert totals["tax_total"] == Decimal("4.00")
    assert totals["grand_total"] == Decimal("54.00")  # 50 + 4 + 0 shipping

def test_cart_totals_with_coupon():
    items = [{"unit_price": Decimal("100.00"), "quantity": 1, "tax_rate": Decimal("0.08")}]
    coupon = {"type": "percentage", "value": Decimal("10")}
    totals = calc_cart_totals(items, coupon)
    assert totals["discount_total"] == Decimal("10.00")

def test_cart_totals_with_shipping():
    items = [{"unit_price": Decimal("50.00"), "quantity": 1, "tax_rate": Decimal("0.08")}]
    totals = calc_cart_totals(items, shipping_cost=Decimal("5.99"))
    assert totals["shipping_total"] == Decimal("5.99")
    assert totals["grand_total"] == Decimal("59.99")  # 50 + 4 + 5.99

def test_free_shipping_coupon_in_totals():
    items = [{"unit_price": Decimal("50.00"), "quantity": 1, "tax_rate": Decimal("0.08")}]
    coupon = {"type": "free_shipping", "value": Decimal("0")}
    totals = calc_cart_totals(items, coupon, shipping_cost=Decimal("12.99"))
    assert totals["shipping_total"] == Decimal("0.00")
