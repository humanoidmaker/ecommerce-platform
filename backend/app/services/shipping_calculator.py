"""Shipping cost calculator — Standard/Express/Overnight with weight-based pricing."""
from __future__ import annotations
from decimal import Decimal
from app.utils.money import money
from app.config import get_settings

# Shipping methods: (name, base_cost, per_kg_cost, min_days, max_days)
SHIPPING_METHODS = {
    "standard": {"name": "Standard Shipping", "base": Decimal("5.99"), "per_kg": Decimal("0.50"), "min_days": 5, "max_days": 7},
    "express": {"name": "Express Shipping", "base": Decimal("12.99"), "per_kg": Decimal("1.00"), "min_days": 2, "max_days": 3},
    "overnight": {"name": "Overnight Shipping", "base": Decimal("24.99"), "per_kg": Decimal("2.00"), "min_days": 1, "max_days": 1},
}


def calculate_shipping(method: str, weight_kg: Decimal, subtotal: Decimal) -> dict:
    """Calculate shipping cost for a method."""
    settings = get_settings()

    if method not in SHIPPING_METHODS:
        raise ValueError(f"Unknown shipping method: {method}")

    m = SHIPPING_METHODS[method]

    # Free shipping for orders over threshold (standard only)
    if method == "standard" and subtotal >= Decimal(str(settings.free_shipping_threshold)):
        return {
            "method": method,
            "name": m["name"],
            "cost": Decimal("0.00"),
            "min_days": m["min_days"],
            "max_days": m["max_days"],
            "free_shipping": True,
        }

    weight = max(weight_kg, Decimal("0.1"))  # Minimum 0.1 kg
    cost = money(m["base"] + m["per_kg"] * weight)

    return {
        "method": method,
        "name": m["name"],
        "cost": cost,
        "min_days": m["min_days"],
        "max_days": m["max_days"],
        "free_shipping": False,
    }


def get_all_shipping_options(weight_kg: Decimal, subtotal: Decimal) -> list[dict]:
    """Get all available shipping methods with costs."""
    return [calculate_shipping(method, weight_kg, subtotal) for method in SHIPPING_METHODS]


def estimate_delivery_date(method: str) -> dict:
    """Estimate delivery date range."""
    from datetime import date, timedelta
    m = SHIPPING_METHODS.get(method)
    if not m:
        return {"earliest": None, "latest": None}
    today = date.today()
    return {
        "earliest": (today + timedelta(days=m["min_days"])).isoformat(),
        "latest": (today + timedelta(days=m["max_days"])).isoformat(),
    }
