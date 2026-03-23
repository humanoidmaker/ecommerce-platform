"""Tests for Decimal money operations — zero floating point."""
from decimal import Decimal
from app.utils.money import money, money_sum, calc_percentage, calc_tax, calc_discount_percentage, calc_commission, calc_seller_payout, format_money


def test_money_from_float():
    assert money(19.99) == Decimal("19.99")

def test_money_from_string():
    assert money("29.995") == Decimal("30.00")  # rounds up

def test_money_from_int():
    assert money(10) == Decimal("10.00")

def test_money_sum_precise():
    values = [Decimal("0.01")] * 100  # 100 pennies
    assert money_sum(values) == Decimal("1.00")

def test_calc_tax():
    assert calc_tax(Decimal("100.00"), Decimal("0.08")) == Decimal("8.00")

def test_calc_tax_rounding():
    assert calc_tax(Decimal("33.33"), Decimal("0.08")) == Decimal("2.67")

def test_calc_discount_percentage():
    assert calc_discount_percentage(Decimal("100.00"), Decimal("20"), None) == Decimal("20.00")

def test_calc_discount_with_max_cap():
    assert calc_discount_percentage(Decimal("1000.00"), Decimal("50"), Decimal("100.00")) == Decimal("100.00")

def test_commission_calculation():
    assert calc_commission(Decimal("200.00"), Decimal("0.15")) == Decimal("30.00")

def test_seller_payout():
    assert calc_seller_payout(Decimal("200.00"), Decimal("30.00")) == Decimal("170.00")

def test_never_lose_cents():
    # 3 items at $33.33, total should be $99.99 not $99.98 or $100.00
    total = money_sum([Decimal("33.33"), Decimal("33.33"), Decimal("33.33")])
    assert total == Decimal("99.99")

def test_format_money_usd():
    assert format_money(Decimal("1234.50"), "USD") == "$1,234.50"
