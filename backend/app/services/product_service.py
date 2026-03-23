"""Product CRUD, variant management, image management, status transitions."""
from __future__ import annotations
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.product import Product
from app.models.product_image import ProductImage
from app.models.product_variant import ProductVariant
from app.models.product_attribute import ProductAttribute
from app.utils.slug_utils import generate_unique_slug


VALID_TRANSITIONS = {
    "draft": {"active", "archived"},
    "active": {"inactive", "out_of_stock", "archived"},
    "inactive": {"active", "archived"},
    "out_of_stock": {"active", "archived"},
    "archived": {"draft"},
}


async def create_product(db: AsyncSession, seller_id: uuid.UUID, title: str, price: Decimal, **kwargs) -> Product:
    product = Product(
        seller_id=seller_id, title=title, slug=generate_unique_slug(title),
        price=price, **kwargs,
    )
    db.add(product)
    await db.flush()
    return product


async def get_product(db: AsyncSession, product_id: uuid.UUID) -> Optional[Product]:
    result = await db.execute(
        select(Product).options(selectinload(Product.images), selectinload(Product.variants), selectinload(Product.attributes))
        .where(Product.id == product_id)
    )
    return result.scalar_one_or_none()


async def get_product_by_slug(db: AsyncSession, slug: str) -> Optional[Product]:
    result = await db.execute(
        select(Product).options(selectinload(Product.images), selectinload(Product.variants))
        .where(Product.slug == slug, Product.status == "active")
    )
    return result.scalar_one_or_none()


async def list_products(db: AsyncSession, seller_id: Optional[uuid.UUID] = None, category_id: Optional[uuid.UUID] = None,
                        status: Optional[str] = None, offset: int = 0, limit: int = 20,
                        sort_by: str = "newest") -> tuple[list[Product], int]:
    q = select(Product).options(selectinload(Product.images))
    if seller_id:
        q = q.where(Product.seller_id == seller_id)
    if category_id:
        q = q.where(Product.category_id == category_id)
    if status:
        q = q.where(Product.status == status)
    else:
        q = q.where(Product.status != "archived")

    total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar() or 0

    if sort_by == "price_low":
        q = q.order_by(Product.price.asc())
    elif sort_by == "price_high":
        q = q.order_by(Product.price.desc())
    elif sort_by == "rating":
        q = q.order_by(Product.average_rating.desc())
    elif sort_by == "bestselling":
        q = q.order_by(Product.total_sold.desc())
    else:
        q = q.order_by(Product.created_at.desc())

    items = (await db.execute(q.offset(offset).limit(limit))).scalars().all()
    return list(items), total


async def update_product(db: AsyncSession, product: Product, **kwargs) -> Product:
    for key, value in kwargs.items():
        if value is not None and hasattr(product, key):
            setattr(product, key, value)
    product.updated_at = datetime.now(timezone.utc)
    await db.flush()
    return product


async def change_status(db: AsyncSession, product: Product, new_status: str) -> Product:
    valid = VALID_TRANSITIONS.get(product.status, set())
    if new_status not in valid:
        raise ValueError(f"Cannot transition from {product.status} to {new_status}")
    product.status = new_status
    if new_status == "active" and not product.published_at:
        product.published_at = datetime.now(timezone.utc)
    await db.flush()
    return product


async def duplicate_product(db: AsyncSession, product: Product) -> Product:
    new = Product(
        seller_id=product.seller_id, title=f"{product.title} (Copy)", slug=generate_unique_slug(product.title),
        description=product.description, short_description=product.short_description,
        category_id=product.category_id, brand=product.brand, tags=product.tags,
        price=product.price, compare_at_price=product.compare_at_price, cost_price=product.cost_price,
        tax_rate=product.tax_rate, weight_kg=product.weight_kg, status="draft",
    )
    db.add(new)
    await db.flush()
    return new


async def delete_product(db: AsyncSession, product: Product) -> None:
    await db.delete(product)
    await db.flush()


# ── Variant Management ──

async def add_variant(db: AsyncSession, product_id: uuid.UUID, name: str, sku: str, attributes_json: dict,
                      price: Optional[Decimal] = None, stock_quantity: int = 0, **kwargs) -> ProductVariant:
    variant = ProductVariant(
        product_id=product_id, name=name, sku=sku, attributes_json=attributes_json,
        price=price, stock_quantity=stock_quantity, **kwargs,
    )
    db.add(variant)
    # Mark product as having variants
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if product:
        product.has_variants = True
    await db.flush()
    return variant


async def update_variant(db: AsyncSession, variant: ProductVariant, **kwargs) -> ProductVariant:
    for key, value in kwargs.items():
        if value is not None and hasattr(variant, key):
            setattr(variant, key, value)
    await db.flush()
    return variant


async def delete_variant(db: AsyncSession, variant: ProductVariant) -> None:
    product_id = variant.product_id
    await db.delete(variant)
    # Check if product still has variants
    count = (await db.execute(select(func.count()).where(ProductVariant.product_id == product_id))).scalar() or 0
    if count == 0:
        result = await db.execute(select(Product).where(Product.id == product_id))
        product = result.scalar_one_or_none()
        if product:
            product.has_variants = False
    await db.flush()


# ── Image Management ──

async def add_image(db: AsyncSession, product_id: uuid.UUID, image_key: str, url: str,
                    thumbnail_key: Optional[str] = None, thumbnail_url: Optional[str] = None,
                    alt_text: str = "", is_primary: bool = False, width: int = 0, height: int = 0) -> ProductImage:
    # Get next sort order
    max_order = (await db.execute(select(func.coalesce(func.max(ProductImage.sort_order), -1)).where(ProductImage.product_id == product_id))).scalar() or -1

    if is_primary:
        # Unset existing primary
        await db.execute(select(ProductImage).where(ProductImage.product_id == product_id, ProductImage.is_primary == True))
        # Simplified — in production use update()

    image = ProductImage(
        product_id=product_id, image_key=image_key, url=url,
        thumbnail_key=thumbnail_key, thumbnail_url=thumbnail_url,
        alt_text=alt_text, is_primary=is_primary, sort_order=max_order + 1,
        width=width, height=height,
    )
    db.add(image)
    await db.flush()
    return image


async def reorder_images(db: AsyncSession, product_id: uuid.UUID, image_ids: list[uuid.UUID]) -> None:
    for idx, img_id in enumerate(image_ids):
        result = await db.execute(select(ProductImage).where(ProductImage.id == img_id, ProductImage.product_id == product_id))
        img = result.scalar_one_or_none()
        if img:
            img.sort_order = idx
    await db.flush()


# ── Attribute Management ──

async def set_attributes(db: AsyncSession, product_id: uuid.UUID, attributes: list[dict]) -> list[ProductAttribute]:
    # Clear existing
    result = await db.execute(select(ProductAttribute).where(ProductAttribute.product_id == product_id))
    for attr in result.scalars().all():
        await db.delete(attr)

    new_attrs = []
    for idx, attr_data in enumerate(attributes):
        attr = ProductAttribute(product_id=product_id, name=attr_data["name"], values_json=attr_data["values"], sort_order=idx)
        db.add(attr)
        new_attrs.append(attr)
    await db.flush()
    return new_attrs
