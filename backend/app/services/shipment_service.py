"""Shipment management — tracking, events, labels, carrier simulation."""
from __future__ import annotations
import uuid
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.shipment import Shipment
from app.models.order_item import OrderItem
from app.utils.order_number import generate_tracking_number
from app.utils.money import money


async def create_shipment(db: AsyncSession, order_id: uuid.UUID, seller_id: uuid.UUID,
                          carrier: str = "internal", weight_kg: Optional[Decimal] = None,
                          warehouse_id: Optional[uuid.UUID] = None) -> Shipment:
    tracking = generate_tracking_number(carrier)
    now = datetime.now(timezone.utc)
    est_delivery = now + timedelta(days=5)

    shipment = Shipment(
        order_id=order_id, seller_id=seller_id, warehouse_id=warehouse_id,
        tracking_number=tracking, carrier=carrier, status="label_created",
        estimated_delivery_date=est_delivery, shipping_cost=money(Decimal("5.99")),
        weight_kg=weight_kg,
        tracking_events_json=[{"status": "label_created", "location": "Warehouse", "timestamp": now.isoformat(), "description": "Shipping label created"}],
    )
    db.add(shipment)
    await db.flush()
    return shipment


async def get_shipment(db: AsyncSession, shipment_id: uuid.UUID) -> Optional[Shipment]:
    return (await db.execute(select(Shipment).where(Shipment.id == shipment_id))).scalar_one_or_none()


async def get_shipments_for_order(db: AsyncSession, order_id: uuid.UUID) -> list[Shipment]:
    return list((await db.execute(select(Shipment).where(Shipment.order_id == order_id))).scalars().all())


async def add_tracking_event(db: AsyncSession, shipment: Shipment, status: str, location: str, description: str) -> Shipment:
    now = datetime.now(timezone.utc)
    events = list(shipment.tracking_events_json or [])
    events.append({"status": status, "location": location, "timestamp": now.isoformat(), "description": description})
    shipment.tracking_events_json = events
    shipment.status = status

    if status == "picked_up":
        shipment.shipped_at = now
    elif status == "delivered":
        shipment.delivered_at = now
        shipment.actual_delivery_date = now

    shipment.updated_at = now
    await db.flush()
    return shipment


async def mark_shipped(db: AsyncSession, shipment: Shipment) -> Shipment:
    return await add_tracking_event(db, shipment, "picked_up", "Distribution Center", "Package picked up by carrier")


async def mark_in_transit(db: AsyncSession, shipment: Shipment, location: str = "In Transit") -> Shipment:
    return await add_tracking_event(db, shipment, "in_transit", location, "Package in transit")


async def mark_delivered(db: AsyncSession, shipment: Shipment) -> Shipment:
    return await add_tracking_event(db, shipment, "delivered", "Destination", "Package delivered")
