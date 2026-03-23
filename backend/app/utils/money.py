"""Decimal money operations — NEVER use float for money."""
from __future__ import annotations
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation

TWOPLACES = Decimal("0.01")
FOURPLACES = Decimal("0.0001")


def money(value: str | int | float | Decimal) -> Decimal:
    """Convert to Decimal rounded to 2 places."""
    try:
        return Decimal(str(value)).quantize(TWOPLACES, rounding=ROUND_HALF_UP)
    except (InvalidOperation, ValueError):
        return Decimal("0.00")


def money_sum(values: list[Decimal | str | int | float]) -> Decimal:
    """Sum values and round to 2 places."""
    total = sum(Decimal(str(v)) for v in values)
    return total.quantize(TWOPLACES, rounding=ROUND_HALF_UP)


def calc_percentage(amount: Decimal, rate: Decimal) -> Decimal:
    """Calculate percentage: amount * rate, rounded to 2 places."""
    return (Decimal(str(amount)) * Decimal(str(rate))).quantize(TWOPLACES, rounding=ROUND_HALF_UP)


def calc_tax(subtotal: Decimal, tax_rate: Decimal) -> Decimal:
    """Calculate tax amount."""
    return calc_percentage(subtotal, tax_rate)


def calc_discount_percentage(amount: Decimal, percentage: Decimal, max_discount: Decimal | None = None) -> Decimal:
    """Calculate percentage discount, with optional cap."""
    discount = calc_percentage(amount, percentage / Decimal("100"))
    if max_discount is not None:
        discount = min(discount, Decimal(str(max_discount)))
    return discount


def calc_commission(order_amount: Decimal, commission_rate: Decimal) -> Decimal:
    """Calculate commission: order_amount * rate."""
    return calc_percentage(order_amount, commission_rate)


def calc_seller_payout(order_amount: Decimal, commission: Decimal) -> Decimal:
    """Seller payout = order amount - commission."""
    return money(Decimal(str(order_amount)) - Decimal(str(commission)))


def format_money(amount: Decimal, currency: str = "USD") -> str:
    """Format for display."""
    symbols = {"USD": "$", "EUR": "€", "GBP": "£", "INR": "₹"}
    symbol = symbols.get(currency, currency + " ")
    return f"{symbol}{amount:,.2f}"
