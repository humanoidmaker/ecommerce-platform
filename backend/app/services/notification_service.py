"""Notification service — create and list notifications."""
from __future__ import annotations
import uuid
from typing import Optional
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.notification import Notification


async def create_notification(db: AsyncSession, user_id: uuid.UUID, type: str, title: str, message: str,
                               action_url: Optional[str] = None, data_json: Optional[dict] = None) -> Notification:
    notif = Notification(user_id=user_id, type=type, title=title, message=message, action_url=action_url, data_json=data_json)
    db.add(notif)
    await db.flush()
    return notif


async def list_notifications(db: AsyncSession, user_id: uuid.UUID, unread_only: bool = False, offset: int = 0, limit: int = 50) -> list[Notification]:
    q = select(Notification).where(Notification.user_id == user_id)
    if unread_only:
        q = q.where(Notification.is_read == False)
    return list((await db.execute(q.order_by(Notification.created_at.desc()).offset(offset).limit(limit))).scalars().all())


async def mark_read(db: AsyncSession, notification_id: uuid.UUID, user_id: uuid.UUID) -> None:
    await db.execute(update(Notification).where(Notification.id == notification_id, Notification.user_id == user_id).values(is_read=True))
    await db.flush()


async def mark_all_read(db: AsyncSession, user_id: uuid.UUID) -> None:
    await db.execute(update(Notification).where(Notification.user_id == user_id, Notification.is_read == False).values(is_read=True))
    await db.flush()


# ── Notification helpers for specific events ──

async def notify_order_placed(db: AsyncSession, buyer_id: uuid.UUID, order_number: str) -> None:
    await create_notification(db, buyer_id, "order_placed", "Order Placed", f"Your order {order_number} has been placed.", f"/orders")


async def notify_order_shipped(db: AsyncSession, buyer_id: uuid.UUID, order_number: str, tracking: str) -> None:
    await create_notification(db, buyer_id, "shipment_update", "Order Shipped", f"Your order {order_number} has been shipped. Tracking: {tracking}", f"/orders")


async def notify_seller_new_order(db: AsyncSession, seller_user_id: uuid.UUID, order_number: str) -> None:
    await create_notification(db, seller_user_id, "order_placed", "New Order", f"You have a new order: {order_number}", "/orders")


async def notify_review_received(db: AsyncSession, seller_user_id: uuid.UUID, product_title: str, rating: int) -> None:
    await create_notification(db, seller_user_id, "review_received", "New Review", f"New {rating}★ review on '{product_title}'", "/reviews")
