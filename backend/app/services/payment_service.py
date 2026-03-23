"""Mock payment gateway — simulates Stripe-like intent→confirm→webhook flow."""
from __future__ import annotations
import uuid
import random
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.payment import Payment
from app.utils.money import money

# Simulated success rate
SUCCESS_RATE = 0.9


def _mock_gateway_id() -> str:
    return f"pi_{uuid.uuid4().hex[:24]}"


async def create_payment_intent(db: AsyncSession, order_id: uuid.UUID, amount: Decimal, currency: str = "USD",
                                 payment_method: str = "card") -> Payment:
    """Create a payment intent (pending). Simulates Stripe's create_payment_intent."""
    payment = Payment(
        order_id=order_id,
        payment_method=payment_method,
        payment_gateway_id=_mock_gateway_id(),
        amount=money(amount),
        currency=currency,
        status="pending",
        gateway_response_json={"mock": True, "created": datetime.now(timezone.utc).isoformat()},
    )
    db.add(payment)
    await db.flush()
    return payment


async def confirm_payment(db: AsyncSession, payment_id: uuid.UUID, force_success: Optional[bool] = None) -> Payment:
    """
    Confirm a payment. Simulates success (90%) or failure (10%).
    Set force_success=True/False for deterministic testing.
    """
    result = await db.execute(select(Payment).where(Payment.id == payment_id))
    payment = result.scalar_one_or_none()
    if not payment:
        raise ValueError("Payment not found")
    if payment.status != "pending":
        raise ValueError(f"Payment already in state: {payment.status}")

    # Simulate gateway confirmation
    success = force_success if force_success is not None else (random.random() < SUCCESS_RATE)

    if success:
        payment.status = "completed"
        payment.paid_at = datetime.now(timezone.utc)
        payment.gateway_response_json = {**(payment.gateway_response_json or {}), "confirmed": True, "status": "succeeded"}
    else:
        payment.status = "failed"
        payment.gateway_response_json = {**(payment.gateway_response_json or {}), "confirmed": False, "status": "failed", "error": "Card declined"}

    await db.flush()
    return payment


async def refund_payment(db: AsyncSession, payment_id: uuid.UUID, amount: Optional[Decimal] = None) -> Payment:
    """Refund a payment (full or partial)."""
    result = await db.execute(select(Payment).where(Payment.id == payment_id))
    payment = result.scalar_one_or_none()
    if not payment:
        raise ValueError("Payment not found")
    if payment.status != "completed":
        raise ValueError("Can only refund completed payments")

    refund_amount = money(amount if amount is not None else payment.amount)
    already_refunded = payment.refund_amount or Decimal("0.00")
    if refund_amount + already_refunded > payment.amount:
        raise ValueError("Refund amount exceeds payment amount")

    payment.refund_amount = money(already_refunded + refund_amount)
    payment.refunded_at = datetime.now(timezone.utc)
    payment.status = "refunded" if payment.refund_amount >= payment.amount else "completed"
    payment.gateway_response_json = {**(payment.gateway_response_json or {}), "refund_amount": str(payment.refund_amount)}

    await db.flush()
    return payment


async def get_payment_by_order(db: AsyncSession, order_id: uuid.UUID) -> Optional[Payment]:
    result = await db.execute(select(Payment).where(Payment.order_id == order_id).order_by(Payment.created_at.desc()))
    return result.scalars().first()
