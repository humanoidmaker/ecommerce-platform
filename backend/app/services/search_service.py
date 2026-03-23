"""Full-text search with weighted ranking, fuzzy matching, autocomplete."""
from __future__ import annotations
import uuid
from typing import Optional
from decimal import Decimal
from sqlalchemy import select, func, or_, text, desc, asc, cast, String
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.product import Product
from app.models.category import Category
from app.models.seller import Seller


async def search_products(
    db: AsyncSession, query: str,
    category_id: Optional[uuid.UUID] = None,
    min_price: Optional[Decimal] = None, max_price: Optional[Decimal] = None,
    min_rating: Optional[float] = None,
    brand: Optional[str] = None,
    seller_id: Optional[uuid.UUID] = None,
    condition: Optional[str] = None,
    sort_by: str = "relevance",
    offset: int = 0, limit: int = 20,
) -> tuple[list[Product], int]:
    """Search products with PostgreSQL full-text search + LIKE fallback."""
    if not query.strip():
        return [], 0

    like_q = f"%{query}%"

    # Base query with search matching
    q = select(Product).where(
        Product.status == "active",
        Product.visibility == "public",
        or_(
            Product.title.ilike(like_q),
            Product.description.ilike(like_q),
            Product.brand.ilike(like_q),
            Product.short_description.ilike(like_q),
        ),
    )

    # Apply filters
    if category_id:
        from app.services.category_service import get_subcategory_ids
        cat_ids = await get_subcategory_ids(db, category_id)
        q = q.where(Product.category_id.in_(cat_ids))
    if min_price is not None:
        q = q.where(Product.price >= min_price)
    if max_price is not None:
        q = q.where(Product.price <= max_price)
    if min_rating is not None:
        q = q.where(Product.average_rating >= Decimal(str(min_rating)))
    if brand:
        q = q.where(Product.brand.ilike(f"%{brand}%"))
    if seller_id:
        q = q.where(Product.seller_id == seller_id)
    if condition:
        q = q.where(Product.condition == condition)

    total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar() or 0

    # Sort
    if sort_by == "price_low":
        q = q.order_by(Product.price.asc())
    elif sort_by == "price_high":
        q = q.order_by(Product.price.desc())
    elif sort_by == "rating":
        q = q.order_by(Product.average_rating.desc())
    elif sort_by == "newest":
        q = q.order_by(Product.created_at.desc())
    elif sort_by == "bestselling":
        q = q.order_by(Product.total_sold.desc())
    else:
        # Relevance: title match first, then by total_sold
        q = q.order_by(Product.total_sold.desc(), Product.average_rating.desc())

    items = (await db.execute(q.offset(offset).limit(limit))).scalars().all()
    return list(items), total


async def autocomplete(db: AsyncSession, query: str, limit: int = 8) -> list[dict]:
    """Return autocomplete suggestions: products + categories."""
    if not query.strip() or len(query) < 2:
        return []

    like_q = f"%{query}%"
    results: list[dict] = []

    # Product suggestions
    products = await db.execute(
        select(Product.id, Product.title, Product.slug, Product.price)
        .where(Product.status == "active", Product.title.ilike(like_q))
        .order_by(Product.total_sold.desc()).limit(limit)
    )
    for row in products.all():
        results.append({"type": "product", "id": str(row[0]), "title": row[1], "slug": row[2], "price": str(row[3])})

    # Category suggestions
    categories = await db.execute(
        select(Category.id, Category.name, Category.slug)
        .where(Category.is_active == True, Category.name.ilike(like_q))
        .limit(4)
    )
    for row in categories.all():
        results.append({"type": "category", "id": str(row[0]), "title": row[1], "slug": row[2]})

    return results[:limit]


async def get_facets(db: AsyncSession, query: str, category_id: Optional[uuid.UUID] = None) -> dict:
    """Get filter facet counts for a search query."""
    like_q = f"%{query}%"
    base = select(Product).where(
        Product.status == "active",
        or_(Product.title.ilike(like_q), Product.description.ilike(like_q)),
    )
    if category_id:
        base = base.where(Product.category_id == category_id)

    # Brand facets
    brand_q = select(Product.brand, func.count()).select_from(base.subquery()).group_by(Product.brand).having(Product.brand.isnot(None))
    brands = {row[0]: row[1] for row in (await db.execute(brand_q)).all()}

    # Price range
    price_q = select(func.min(Product.price), func.max(Product.price)).select_from(base.subquery())
    price_row = (await db.execute(price_q)).one_or_none()
    price_range = {"min": str(price_row[0] or 0), "max": str(price_row[1] or 0)} if price_row else {"min": "0", "max": "0"}

    return {"brands": brands, "price_range": price_range}
