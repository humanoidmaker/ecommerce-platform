"""Category tree management, breadcrumbs, product counts."""
from __future__ import annotations
import uuid
from typing import Optional
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.category import Category
from app.models.product import Product
from app.utils.slug_utils import generate_slug


async def create_category(db: AsyncSession, name: str, parent_id: Optional[uuid.UUID] = None, **kwargs) -> Category:
    depth = 0
    if parent_id:
        parent = await get_category(db, parent_id)
        if parent:
            depth = parent.depth + 1
            if depth > 2:
                raise ValueError("Maximum category depth is 3 levels (0, 1, 2)")

    slug = generate_slug(name)
    # Ensure unique slug
    existing = await db.execute(select(Category).where(Category.slug == slug))
    if existing.scalar_one_or_none():
        slug = f"{slug}-{uuid.uuid4().hex[:6]}"

    cat = Category(name=name, slug=slug, parent_category_id=parent_id, depth=depth, **kwargs)
    db.add(cat)
    await db.flush()
    return cat


async def get_category(db: AsyncSession, category_id: uuid.UUID) -> Optional[Category]:
    result = await db.execute(select(Category).where(Category.id == category_id))
    return result.scalar_one_or_none()


async def get_category_by_slug(db: AsyncSession, slug: str) -> Optional[Category]:
    result = await db.execute(select(Category).where(Category.slug == slug, Category.is_active == True))
    return result.scalar_one_or_none()


async def list_categories(db: AsyncSession, parent_id: Optional[uuid.UUID] = None, active_only: bool = True) -> list[Category]:
    q = select(Category).where(Category.parent_category_id == parent_id)
    if active_only:
        q = q.where(Category.is_active == True)
    result = await db.execute(q.order_by(Category.sort_order, Category.name))
    return list(result.scalars().all())


async def list_all_categories(db: AsyncSession) -> list[Category]:
    result = await db.execute(select(Category).where(Category.is_active == True).order_by(Category.depth, Category.sort_order, Category.name))
    return list(result.scalars().all())


async def get_category_tree(db: AsyncSession) -> list[dict]:
    """Return full category tree as nested dicts."""
    all_cats = await list_all_categories(db)
    cat_map = {c.id: {"id": c.id, "name": c.name, "slug": c.slug, "depth": c.depth, "product_count": c.product_count, "children": []} for c in all_cats}

    roots = []
    for c in all_cats:
        node = cat_map[c.id]
        if c.parent_category_id and c.parent_category_id in cat_map:
            cat_map[c.parent_category_id]["children"].append(node)
        else:
            roots.append(node)
    return roots


async def get_breadcrumb(db: AsyncSession, category_id: uuid.UUID) -> list[dict]:
    """Get breadcrumb path from root to category."""
    path = []
    current_id: Optional[uuid.UUID] = category_id
    while current_id:
        cat = await get_category(db, current_id)
        if not cat:
            break
        path.append({"id": cat.id, "name": cat.name, "slug": cat.slug})
        current_id = cat.parent_category_id
    path.reverse()
    return path


async def get_subcategory_ids(db: AsyncSession, category_id: uuid.UUID) -> list[uuid.UUID]:
    """Get all descendant category IDs (for filtering products by category including subs)."""
    ids = [category_id]
    children = await db.execute(select(Category.id).where(Category.parent_category_id == category_id))
    for (child_id,) in children.all():
        ids.append(child_id)
        grandchildren = await db.execute(select(Category.id).where(Category.parent_category_id == child_id))
        for (gc_id,) in grandchildren.all():
            ids.append(gc_id)
    return ids


async def update_category(db: AsyncSession, category: Category, **kwargs) -> Category:
    for key, value in kwargs.items():
        if value is not None and hasattr(category, key):
            setattr(category, key, value)
    await db.flush()
    return category


async def recount_products(db: AsyncSession, category_id: uuid.UUID) -> int:
    """Recount products in category and update denormalized count."""
    count = (await db.execute(select(func.count()).where(Product.category_id == category_id, Product.status == "active"))).scalar() or 0
    await db.execute(update(Category).where(Category.id == category_id).values(product_count=count))
    await db.flush()
    return count


async def delete_category(db: AsyncSession, category: Category) -> None:
    # Check for products
    count = (await db.execute(select(func.count()).where(Product.category_id == category.id))).scalar() or 0
    if count > 0:
        raise ValueError(f"Cannot delete category with {count} products")
    # Check for children
    children_count = (await db.execute(select(func.count()).where(Category.parent_category_id == category.id))).scalar() or 0
    if children_count > 0:
        raise ValueError(f"Cannot delete category with {children_count} subcategories")
    await db.delete(category)
    await db.flush()
