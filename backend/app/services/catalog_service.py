"""Catalog service — home page assembly, category listings, product detail."""
from __future__ import annotations
import uuid
from typing import Optional
from decimal import Decimal
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.product import Product
from app.models.product_image import ProductImage
from app.models.category import Category
from app.models.seller import Seller
from app.models.review import Review


async def get_home_page(db: AsyncSession) -> dict:
    """Assemble home page data: featured, bestsellers, deals, categories."""
    # Featured products
    featured = await db.execute(
        select(Product).options(selectinload(Product.images))
        .where(Product.status == "active", Product.is_featured == True)
        .order_by(Product.updated_at.desc()).limit(8)
    )

    # Bestsellers
    bestsellers = await db.execute(
        select(Product).options(selectinload(Product.images))
        .where(Product.status == "active", Product.is_bestseller == True)
        .order_by(Product.total_sold.desc()).limit(8)
    )

    # Deals (products with compare_at_price)
    deals = await db.execute(
        select(Product).options(selectinload(Product.images))
        .where(Product.status == "active", Product.compare_at_price.isnot(None), Product.compare_at_price > Product.price)
        .order_by(func.random()).limit(8)
    )

    # Top categories
    categories = await db.execute(
        select(Category).where(Category.is_active == True, Category.depth == 0)
        .order_by(Category.sort_order).limit(12)
    )

    # New arrivals
    new_arrivals = await db.execute(
        select(Product).options(selectinload(Product.images))
        .where(Product.status == "active")
        .order_by(Product.published_at.desc().nullslast()).limit(8)
    )

    return {
        "featured": list(featured.scalars().all()),
        "bestsellers": list(bestsellers.scalars().all()),
        "deals": list(deals.scalars().all()),
        "categories": list(categories.scalars().all()),
        "new_arrivals": list(new_arrivals.scalars().all()),
    }


async def get_category_page(db: AsyncSession, category_id: uuid.UUID, offset: int = 0, limit: int = 20,
                            sort_by: str = "newest", min_price: Optional[Decimal] = None,
                            max_price: Optional[Decimal] = None, min_rating: Optional[float] = None) -> dict:
    """Get products for a category page with filters."""
    from app.services.category_service import get_subcategory_ids, get_breadcrumb, get_category, list_categories

    cat = await get_category(db, category_id)
    if not cat:
        return {"category": None, "products": [], "total": 0}

    cat_ids = await get_subcategory_ids(db, category_id)
    subcategories = await list_categories(db, parent_id=category_id)
    breadcrumb = await get_breadcrumb(db, category_id)

    q = select(Product).options(selectinload(Product.images)).where(Product.status == "active", Product.category_id.in_(cat_ids))

    if min_price is not None:
        q = q.where(Product.price >= min_price)
    if max_price is not None:
        q = q.where(Product.price <= max_price)
    if min_rating is not None:
        q = q.where(Product.average_rating >= Decimal(str(min_rating)))

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

    products = (await db.execute(q.offset(offset).limit(limit))).scalars().all()

    return {
        "category": cat,
        "subcategories": subcategories,
        "breadcrumb": breadcrumb,
        "products": list(products),
        "total": total,
    }


async def get_product_detail(db: AsyncSession, product_id: uuid.UUID) -> Optional[dict]:
    """Full product detail page data."""
    from app.services.product_service import get_product

    product = await get_product(db, product_id)
    if not product or product.status != "active":
        return None

    # Seller info
    seller = await db.execute(select(Seller).where(Seller.id == product.seller_id))
    seller_data = seller.scalar_one_or_none()

    # Review summary
    rating_dist = {}
    for star in range(1, 6):
        count = (await db.execute(select(func.count()).where(Review.product_id == product_id, Review.rating == star, Review.is_hidden == False))).scalar() or 0
        rating_dist[star] = count

    # Related products (same category)
    related = await db.execute(
        select(Product).options(selectinload(Product.images))
        .where(Product.category_id == product.category_id, Product.id != product_id, Product.status == "active")
        .order_by(Product.total_sold.desc()).limit(6)
    )

    # Increment view count
    product.view_count += 1
    await db.flush()

    return {
        "product": product,
        "seller": seller_data,
        "rating_distribution": rating_dist,
        "related_products": list(related.scalars().all()),
    }
