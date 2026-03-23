"""Pricing engine — item prices, coupons, tax, shipping, totals. ALL Decimal, NEVER float."""
from __future__ import annotations
from decimal import Decimal
from typing import Optional
from app.utils.money import money, money_sum, calc_tax, calc_discount_percentage


def get_item_price(product_price: Decimal, variant_price: Optional[Decimal] = None) -> Decimal:
    """Get effective price: variant override or product base price."""
    return money(variant_price if variant_price is not None else product_price)


def calc_line_total(unit_price: Decimal, quantity: int) -> Decimal:
    return money(Decimal(str(unit_price)) * quantity)


def apply_coupon(subtotal: Decimal, coupon_type: str, coupon_value: Decimal,
                 min_order: Optional[Decimal] = None, max_discount: Optional[Decimal] = None) -> Decimal:
    """Calculate discount from coupon. Returns discount amount (not new subtotal)."""
    if min_order is not None and subtotal < min_order:
        return Decimal("0.00")

    if coupon_type == "percentage":
        discount = calc_discount_percentage(subtotal, coupon_value, max_discount)
    elif coupon_type == "fixed_amount":
        discount = money(min(coupon_value, subtotal))
    elif coupon_type == "free_shipping":
        return Decimal("0.00")  # Handled separately in shipping
    else:
        return Decimal("0.00")

    return discount


def calc_cart_totals(items: list[dict], coupon: Optional[dict] = None,
                     shipping_cost: Decimal = Decimal("0.00"), tax_rate: Decimal = Decimal("0.08")) -> dict:
    """
    Calculate full cart totals.
    items: [{"unit_price": Decimal, "quantity": int, "tax_rate": Decimal}]
    coupon: {"type": str, "value": Decimal, "min_order": Decimal|None, "max_discount": Decimal|None}
    """
    # Subtotal
    subtotal = money_sum([calc_line_total(i["unit_price"], i["quantity"]) for i in items])

    # Coupon discount
    discount = Decimal("0.00")
    if coupon:
        discount = apply_coupon(subtotal, coupon["type"], coupon["value"],
                                coupon.get("min_order"), coupon.get("max_discount"))

    # Tax (on subtotal after discount)
    taxable = money(subtotal - discount)
    tax_total = Decimal("0.00")
    for item in items:
        item_tax_rate = item.get("tax_rate", tax_rate)
        item_total = calc_line_total(item["unit_price"], item["quantity"])
        tax_total = money(tax_total + calc_tax(item_total, item_tax_rate))

    # Shipping (free if coupon is free_shipping type)
    effective_shipping = shipping_cost
    if coupon and coupon.get("type") == "free_shipping":
        effective_shipping = Decimal("0.00")

    # Grand total
    grand_total = money(subtotal - discount + tax_total + effective_shipping)
    grand_total = max(grand_total, Decimal("0.00"))

    return {
        "subtotal": subtotal,
        "discount_total": discount,
        "tax_total": tax_total,
        "shipping_total": effective_shipping,
        "grand_total": grand_total,
        "item_count": sum(i["quantity"] for i in items),
    }
