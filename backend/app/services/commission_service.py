"""Commission calculation and payout generation."""
from __future__ import annotations
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.commission import Commission
from app.models.payout import Payout
from app.models.order_item import OrderItem
from app.utils.money import money, calc_commission, calc_seller_payout
from app.utils.order_number import generate_payout_reference


async def calculate_commission(db: AsyncSession, order_item: OrderItem) -> Commission:
    """Calculate commission for a completed order item."""
    comm_amount = calc_commission(order_item.total_price, order_item.commission_rate)
    seller_pay = calc_seller_payout(order_item.total_price, comm_amount)

    commission = Commission(
        order_item_id=order_item.id, seller_id=order_item.seller_id,
        order_total=order_item.total_price, commission_rate=order_item.commission_rate,
        commission_amount=comm_amount, platform_fee=comm_amount,
        seller_payout=seller_pay, status="calculated",
        calculated_at=datetime.now(timezone.utc),
    )
    db.add(commission)
    await db.flush()
    return commission


async def generate_seller_payout(db: AsyncSession, seller_id: uuid.UUID,
                                  period_start: datetime, period_end: datetime) -> Optional[Payout]:
    """Generate payout for all calculated commissions in period."""
    commissions = (await db.execute(
        select(Commission).where(
            Commission.seller_id == seller_id, Commission.status == "calculated",
            Commission.calculated_at >= period_start, Commission.calculated_at <= period_end,
        )
    )).scalars().all()

    if not commissions:
        return None

    total_payout = money(sum(c.seller_payout for c in commissions))
    payout = Payout(
        seller_id=seller_id, amount=total_payout, period_start=period_start,
        period_end=period_end, items_count=len(commissions),
        payout_reference=generate_payout_reference(), status="pending",
    )
    db.add(payout)
    await db.flush()

    # Link commissions to payout
    for c in commissions:
        c.payout_id = payout.id
        c.status = "paid_out"
        c.paid_at = datetime.now(timezone.utc)
    await db.flush()

    return payout


async def get_seller_commission_summary(db: AsyncSession, seller_id: uuid.UUID) -> dict:
    """Get commission summary for a seller."""
    total_revenue = (await db.execute(select(func.coalesce(func.sum(Commission.order_total), 0)).where(Commission.seller_id == seller_id))).scalar() or Decimal("0")
    total_commission = (await db.execute(select(func.coalesce(func.sum(Commission.commission_amount), 0)).where(Commission.seller_id == seller_id))).scalar() or Decimal("0")
    total_payout = (await db.execute(select(func.coalesce(func.sum(Commission.seller_payout), 0)).where(Commission.seller_id == seller_id))).scalar() or Decimal("0")
    pending = (await db.execute(select(func.coalesce(func.sum(Commission.seller_payout), 0)).where(Commission.seller_id == seller_id, Commission.status == "calculated"))).scalar() or Decimal("0")

    return {
        "total_revenue": str(total_revenue),
        "total_commission": str(total_commission),
        "total_payout": str(total_payout),
        "pending_payout": str(pending),
    }


async def list_seller_payouts(db: AsyncSession, seller_id: uuid.UUID) -> list[Payout]:
    return list((await db.execute(select(Payout).where(Payout.seller_id == seller_id).order_by(Payout.created_at.desc()))).scalars().all())
