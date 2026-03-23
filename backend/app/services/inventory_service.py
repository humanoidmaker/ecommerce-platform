"""Inventory management — stock tracking, reservation, release, atomic operations."""
from __future__ import annotations
import uuid
from typing import Optional
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.product import Product
from app.models.product_variant import ProductVariant


class InsufficientStockError(Exception):
    def __init__(self, product_id: uuid.UUID, available: int, requested: int):
        self.product_id = product_id
        self.available = available
        self.requested = requested
        super().__init__(f"Insufficient stock: available={available}, requested={requested}")


async def get_available_stock(db: AsyncSession, product_id: uuid.UUID, variant_id: Optional[uuid.UUID] = None) -> int:
    """Get available stock (quantity - reserved)."""
    if variant_id:
        result = await db.execute(select(ProductVariant).where(ProductVariant.id == variant_id))
        variant = result.scalar_one_or_none()
        if not variant:
            return 0
        return max(0, variant.stock_quantity - variant.reserved_quantity)
    # No variant — product-level stock not tracked separately in this schema
    # Sum all variant stocks if has_variants
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        return 0
    if product.has_variants:
        variants = (await db.execute(select(ProductVariant).where(ProductVariant.product_id == product_id, ProductVariant.is_active == True))).scalars().all()
        return sum(max(0, v.stock_quantity - v.reserved_quantity) for v in variants)
    return 999  # Non-variant products have unlimited stock by default


async def reserve_stock(db: AsyncSession, product_id: uuid.UUID, variant_id: Optional[uuid.UUID], quantity: int) -> None:
    """Reserve stock for checkout. Raises InsufficientStockError if not enough."""
    if variant_id:
        result = await db.execute(select(ProductVariant).where(ProductVariant.id == variant_id))
        variant = result.scalar_one_or_none()
        if not variant:
            raise InsufficientStockError(product_id, 0, quantity)
        available = variant.stock_quantity - variant.reserved_quantity
        if available < quantity:
            raise InsufficientStockError(product_id, available, quantity)
        variant.reserved_quantity += quantity
        await db.flush()
        return

    # Non-variant product — no stock tracking
    return


async def release_stock(db: AsyncSession, product_id: uuid.UUID, variant_id: Optional[uuid.UUID], quantity: int) -> None:
    """Release reserved stock (on cancel/payment failure)."""
    if variant_id:
        result = await db.execute(select(ProductVariant).where(ProductVariant.id == variant_id))
        variant = result.scalar_one_or_none()
        if variant:
            variant.reserved_quantity = max(0, variant.reserved_quantity - quantity)
            await db.flush()


async def deduct_stock(db: AsyncSession, product_id: uuid.UUID, variant_id: Optional[uuid.UUID], quantity: int) -> None:
    """Deduct stock when shipped (convert reservation to actual deduction)."""
    if variant_id:
        result = await db.execute(select(ProductVariant).where(ProductVariant.id == variant_id))
        variant = result.scalar_one_or_none()
        if variant:
            variant.stock_quantity = max(0, variant.stock_quantity - quantity)
            variant.reserved_quantity = max(0, variant.reserved_quantity - quantity)
            # Check if out of stock
            if variant.stock_quantity <= 0:
                product = (await db.execute(select(Product).where(Product.id == product_id))).scalar_one_or_none()
                if product:
                    # Check all variants
                    total = (await db.execute(select(ProductVariant).where(ProductVariant.product_id == product_id))).scalars().all()
                    if all(v.stock_quantity <= 0 for v in total):
                        product.status = "out_of_stock"
            await db.flush()


async def restock(db: AsyncSession, variant_id: uuid.UUID, quantity: int) -> int:
    """Add stock to a variant. Returns new quantity."""
    result = await db.execute(select(ProductVariant).where(ProductVariant.id == variant_id))
    variant = result.scalar_one_or_none()
    if not variant:
        raise ValueError("Variant not found")
    variant.stock_quantity += quantity
    from datetime import datetime, timezone
    variant.last_restocked_at = datetime.now(timezone.utc)

    # If product was out_of_stock, set back to active
    product = (await db.execute(select(Product).where(Product.id == variant.product_id))).scalar_one_or_none()
    if product and product.status == "out_of_stock":
        product.status = "active"

    await db.flush()
    return variant.stock_quantity


async def get_low_stock_variants(db: AsyncSession, seller_id: Optional[uuid.UUID] = None) -> list[ProductVariant]:
    """Get variants where stock is at or below threshold."""
    q = select(ProductVariant).where(ProductVariant.stock_quantity <= ProductVariant.low_stock_threshold, ProductVariant.is_active == True)
    if seller_id:
        q = q.join(Product).where(Product.seller_id == seller_id)
    result = await db.execute(q)
    return list(result.scalars().all())
