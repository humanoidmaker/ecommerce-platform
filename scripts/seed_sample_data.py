import asyncio
import sys
import uuid
import random
from datetime import datetime, timezone, timedelta
from decimal import Decimal

sys.path.insert(0, ".")

from app.database import async_session_factory, engine, Base
from app.models.user import User
from app.models.seller import Seller
from app.models.category import Category
from app.models.product import Product
from app.models.product_image import ProductImage
from app.models.product_variant import ProductVariant
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.review import Review
from app.models.coupon import Coupon
from app.utils.hashing import hash_password


CATEGORIES = {
    "Electronics": ["Smartphones", "Laptops", "Accessories", "Audio"],
    "Clothing": ["Men", "Women", "Kids"],
    "Home & Kitchen": ["Appliances", "Bedding", "Cookware"],
    "Books": [],
    "Sports": [],
}

PRODUCTS = [
    # Electronics
    {"title": "NovaTech Prism X Pro", "slug": "novatech-prism-x-pro", "category": "Smartphones", "brand": "NovaTech", "price": 134999, "compare_at": 144999, "description": "A premium flagship smartphone featuring a built-in stylus, 200MP camera system, and latest-generation processor.", "short": "Flagship smartphone with stylus", "featured": True, "bestseller": True, "variants": [("Storage: 256GB", 134999, 50), ("Storage: 512GB", 154999, 30)]},
    {"title": "ZenBook AirLite 15", "slug": "zenbook-airlite-15", "category": "Laptops", "brand": "ZenTech", "price": 114900, "compare_at": 124900, "description": "An ultra-thin laptop powered by a next-generation chip for outstanding performance and all-day battery life.", "short": "Ultra-thin high-performance laptop", "featured": True, "variants": [("RAM: 8GB, Storage: 256GB", 114900, 25), ("RAM: 16GB, Storage: 512GB", 144900, 15)]},
    {"title": "SoundWave Elite ANC Headphones", "slug": "soundwave-elite-anc", "category": "Audio", "brand": "SoundWave", "price": 24990, "compare_at": 29990, "description": "Premium over-ear headphones with advanced active noise cancellation and hi-fi audio drivers.", "short": "Premium noise-cancelling headphones", "featured": True, "variants": [("Color: Black", 24990, 80), ("Color: Silver", 24990, 45)]},
    {"title": "BoomBox Mini X Bluetooth Speaker", "slug": "boombox-mini-x", "category": "Audio", "brand": "BoomBox", "price": 9999, "description": "Compact portable speaker with bold sound output and IP67 waterproof rating.", "short": "Portable waterproof speaker", "variants": [("Color: Black", 9999, 100), ("Color: Red", 9999, 60), ("Color: Blue", 9999, 75)]},
    {"title": "PulseBand Fit 2", "slug": "pulseband-fit-2", "category": "Accessories", "brand": "PulseBand", "price": 29900, "description": "A versatile smartwatch with health tracking, fitness monitoring, and seamless notifications.", "short": "Essential smartwatch", "variants": [("Size: 40mm", 29900, 40), ("Size: 44mm", 33900, 35)]},
    # Clothing
    {"title": "UrbanThread Premium Cotton Shirt", "slug": "urbanthread-cotton-shirt", "category": "Men", "brand": "UrbanThread", "price": 1499, "compare_at": 2199, "description": "Classic fit premium cotton formal shirt perfect for office and casual wear.", "short": "Premium cotton formal shirt", "featured": True, "variants": [("Size: M, Color: White", 1499, 50), ("Size: L, Color: White", 1499, 40), ("Size: M, Color: Blue", 1499, 35), ("Size: L, Color: Blue", 1499, 30)]},
    {"title": "DenimCraft 511 Slim Fit Jeans", "slug": "denimcraft-511-slim-jeans", "category": "Men", "brand": "DenimCraft", "price": 2999, "compare_at": 3999, "description": "Modern slim fit jeans with stretch comfort technology for everyday wear.", "short": "Classic slim fit jeans", "bestseller": True, "variants": [("Size: 30, Color: Indigo", 2999, 25), ("Size: 32, Color: Indigo", 2999, 30), ("Size: 34, Color: Black", 2999, 20)]},
    {"title": "SwiftStride Revolution 6 Running Shoes", "slug": "swiftstride-revolution-6", "category": "Men", "brand": "SwiftStride", "price": 3695, "description": "Lightweight running shoes with cushioned midsole for everyday comfort.", "short": "Lightweight running shoes", "variants": [("Size: 8, Color: Black", 3695, 40), ("Size: 9, Color: Black", 3695, 45), ("Size: 10, Color: White", 3695, 35)]},
    {"title": "HandLoom Co Embroidered Cotton Kurti", "slug": "handloom-co-cotton-kurti", "category": "Women", "brand": "HandLoom Co", "price": 1799, "compare_at": 2499, "description": "Hand-embroidered cotton kurti with traditional artisan motifs.", "short": "Handcrafted cotton kurti", "featured": True, "variants": [("Size: S, Color: Indigo", 1799, 30), ("Size: M, Color: Indigo", 1799, 40), ("Size: L, Color: Maroon", 1799, 25)]},
    {"title": "TailorEdge Classic Fit Blazer", "slug": "tailoredge-classic-blazer", "category": "Men", "brand": "TailorEdge", "price": 7999, "compare_at": 11999, "description": "Premium wool-blend blazer for formal occasions and business meetings.", "short": "Premium formal blazer", "variants": [("Size: 38", 7999, 15), ("Size: 40", 7999, 20), ("Size: 42", 7999, 12)]},
    # Home & Kitchen
    {"title": "KitchenPro Iris 750W Mixer Grinder", "slug": "kitchenpro-iris-mixer", "category": "Appliances", "brand": "KitchenPro", "price": 3499, "compare_at": 4999, "description": "Powerful 750W motor with 3 stainless steel jars for all your grinding needs.", "short": "750W mixer grinder", "bestseller": True, "variants": [("Color: White/Blue", 3499, 60)]},
    {"title": "CleanAir AC1215 Air Purifier", "slug": "cleanair-ac1215-purifier", "category": "Appliances", "brand": "CleanAir", "price": 9999, "description": "Advanced filtration technology removes 99.97% of airborne pollutants for cleaner indoor air.", "short": "HEPA air purifier", "variants": [("Standard", 9999, 25)]},
    {"title": "SleepWell Floral Bedsheet Set", "slug": "sleepwell-bedsheet", "category": "Bedding", "brand": "SleepWell", "price": 1299, "compare_at": 1999, "description": "100% cotton king-size bedsheet with 2 pillow covers.", "short": "Cotton king-size bedsheet", "variants": [("Color: Blue Floral", 1299, 80), ("Color: Pink Floral", 1299, 65)]},
    {"title": "ThermoFlask Insulated Flask 1L", "slug": "thermoflask-insulated-1l", "category": "Cookware", "brand": "ThermoFlask", "price": 799, "description": "Double-wall vacuum insulated flask that keeps beverages hot for 24 hours.", "short": "1L vacuum flask", "variants": [("Color: Silver", 799, 120), ("Color: Black", 799, 90)]},
    {"title": "CookEase Joy Rice Cooker 1.8L", "slug": "cookease-joy-rice-cooker", "category": "Appliances", "brand": "CookEase", "price": 1599, "description": "Electric rice cooker with aluminium cooking pot and automatic keep-warm function.", "short": "1.8L electric rice cooker", "variants": [("Standard", 1599, 55)]},
    # Books
    {"title": "Atomic Habits by James Clear", "slug": "atomic-habits", "category": "Books", "brand": "BookHouse", "price": 499, "compare_at": 699, "description": "A practical guide to building good habits and breaking bad ones.", "short": "Bestselling self-help book", "featured": True, "bestseller": True, "variants": [("Paperback", 499, 200), ("Hardcover", 899, 50)]},
    {"title": "Sapiens by Yuval Noah Harari", "slug": "sapiens-harari", "category": "Books", "brand": "PageTurner", "price": 549, "description": "A sweeping narrative exploring the history of humankind from ancient times to the present.", "short": "History of humankind", "variants": [("Paperback", 549, 150)]},
    {"title": "The Psychology of Money", "slug": "psychology-of-money", "category": "Books", "brand": "MindPress", "price": 399, "compare_at": 499, "description": "Timeless lessons on wealth, greed, and happiness through the lens of behavioral finance.", "short": "Finance and psychology", "variants": [("Paperback", 399, 180)]},
    # Sports
    {"title": "AceSport Nanoray Light 18i Racket", "slug": "acesport-nanoray-racket", "category": "Sports", "brand": "AceSport", "price": 2490, "description": "Lightweight badminton racket with isometric head shape for powerful shots.", "short": "Lightweight badminton racket", "variants": [("Standard", 2490, 40)]},
    {"title": "SportKick Storm Football Size 5", "slug": "sportkick-storm-football", "category": "Sports", "brand": "SportKick", "price": 699, "description": "Machine-stitched training football suitable for all surfaces.", "short": "Training football", "variants": [("Size: 5", 699, 75)]},
]

REVIEWS = [
    ("Amazing product! Totally worth the price.", 5),
    ("Good quality but delivery was a bit slow.", 4),
    ("Very comfortable and fits perfectly.", 5),
    ("Decent product for the price range.", 3),
    ("Excellent build quality, highly recommended!", 5),
    ("Color is slightly different from the image.", 3),
    ("My go-to brand, never disappoints.", 5),
    ("Value for money purchase.", 4),
    ("Could be better, expected more.", 2),
    ("Superb quality material, will buy again.", 5),
    ("Fast delivery, product as described.", 4),
    ("Perfect gift for my family.", 5),
    ("Average quality, nothing special.", 3),
    ("Absolutely love it! Best purchase this month.", 5),
    ("Good product but packaging could improve.", 4),
]


async def seed_sample_data():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_factory() as session:
        from sqlalchemy import select

        result = await session.execute(select(Category))
        if result.scalars().first():
            print("Sample data already exists.")
            return

        now = datetime.now(timezone.utc)

        # 1. Create buyers
        buyers = []
        buyer_data = [
            ("Rahul", "Kumar", "rahul@example.com", "+919876543210"),
            ("Anita", "Patel", "anita@example.com", "+919876543211"),
            ("Vikram", "Singh", "vikram@example.com", "+919876543212"),
        ]
        for fn, ln, email, phone in buyer_data:
            user = User(id=uuid.uuid4(), email=email, password_hash=hash_password("user123"), first_name=fn, last_name=ln, phone=phone, role="buyer", is_active=True, email_verified=True)
            session.add(user)
            buyers.append(user)
        await session.flush()
        print(f"Created {len(buyers)} buyers")

        # 2. Create sellers
        result = await session.execute(select(User).where(User.email == "admin@ecommerce.local"))
        admin = result.scalar_one_or_none()

        seller_user1 = User(id=uuid.uuid4(), email="gadgetzone@ecommerce.local", password_hash=hash_password("seller123"), first_name="Priya", last_name="Sharma", role="seller", is_active=True, email_verified=True)
        seller_user2 = User(id=uuid.uuid4(), email="stylevault@ecommerce.local", password_hash=hash_password("seller123"), first_name="Amit", last_name="Verma", role="seller", is_active=True, email_verified=True)
        session.add_all([seller_user1, seller_user2])
        await session.flush()

        seller1 = Seller(id=uuid.uuid4(), user_id=seller_user1.id, store_name="GadgetZone", store_slug="gadgetzone", store_description="Premium electronics and gadgets at the best prices.", is_verified=True, is_featured=True, application_status="approved")
        seller2 = Seller(id=uuid.uuid4(), user_id=seller_user2.id, store_name="StyleVault", store_slug="stylevault", store_description="Trendy fashion for men, women, and kids.", is_verified=True, application_status="approved")
        session.add_all([seller1, seller2])
        await session.flush()
        print("Created 2 sellers")

        # 3. Create categories
        cat_map = {}
        sort = 0
        for parent_name, children in CATEGORIES.items():
            parent_slug = parent_name.lower().replace(" & ", "-").replace(" ", "-")
            parent = Category(id=uuid.uuid4(), name=parent_name, slug=parent_slug, is_active=True, sort_order=sort, depth=0)
            session.add(parent)
            await session.flush()
            cat_map[parent_name] = parent
            sort += 1
            for child_name in children:
                child_slug = child_name.lower().replace(" ", "-")
                child = Category(id=uuid.uuid4(), name=child_name, slug=child_slug, parent_category_id=parent.id, is_active=True, sort_order=sort, depth=1)
                session.add(child)
                await session.flush()
                cat_map[child_name] = child
                sort += 1
        print(f"Created {len(cat_map)} categories")

        # 4. Create products
        products = []
        for p_data in PRODUCTS:
            cat = cat_map.get(p_data["category"])
            seller = seller1 if p_data["category"] in ["Smartphones", "Laptops", "Accessories", "Audio", "Books", "Sports", "Appliances", "Cookware"] else seller2
            product = Product(
                id=uuid.uuid4(), seller_id=seller.id, title=p_data["title"], slug=p_data["slug"],
                description=p_data["description"], short_description=p_data.get("short", ""),
                category_id=cat.id if cat else None, brand=p_data.get("brand", ""),
                price=Decimal(str(p_data["price"])),
                compare_at_price=Decimal(str(p_data["compare_at"])) if p_data.get("compare_at") else None,
                currency="INR", status="active", is_featured=p_data.get("featured", False),
                is_bestseller=p_data.get("bestseller", False), has_variants=len(p_data.get("variants", [])) > 1,
                published_at=now - timedelta(days=random.randint(1, 90)),
            )
            session.add(product)
            await session.flush()

            # Image
            img = ProductImage(id=uuid.uuid4(), product_id=product.id, image_url=f"https://placehold.co/600x600/EEE/333?text={p_data['slug']}", alt_text=p_data["title"], sort_order=0, is_primary=True)
            session.add(img)

            # Variants
            for vi, (vname, vprice, vstock) in enumerate(p_data.get("variants", [])):
                sku = f"{p_data['brand'][:3].upper()}-{p_data['slug'][:5].upper()}-{vi}"
                variant = ProductVariant(id=uuid.uuid4(), product_id=product.id, sku=sku, name=vname, price=Decimal(str(vprice)), stock_quantity=vstock, sort_order=vi)
                session.add(variant)

            products.append(product)

        await session.flush()
        print(f"Created {len(products)} products")

        # 5. Create reviews
        for i, (comment, rating) in enumerate(REVIEWS):
            product = random.choice(products)
            buyer = buyers[i % len(buyers)]
            review = Review(id=uuid.uuid4(), buyer_id=buyer.id, product_id=product.id, rating=rating, title=comment[:40], comment=comment, is_verified=random.random() > 0.3)
            session.add(review)
        print(f"Created {len(REVIEWS)} reviews")

        # 6. Create coupons
        coupons = [
            Coupon(id=uuid.uuid4(), code="WELCOME10", discount_type="percentage", discount_value=Decimal("10"), min_order_amount=Decimal("999"), max_discount=Decimal("500"), max_uses=1000, is_active=True, valid_from=now - timedelta(days=30), valid_until=now + timedelta(days=365)),
            Coupon(id=uuid.uuid4(), code="FLAT500", discount_type="fixed", discount_value=Decimal("500"), min_order_amount=Decimal("2999"), max_uses=500, is_active=True, valid_from=now - timedelta(days=30), valid_until=now + timedelta(days=365)),
            Coupon(id=uuid.uuid4(), code="SUMMER20", discount_type="percentage", discount_value=Decimal("20"), min_order_amount=Decimal("1499"), max_discount=Decimal("1000"), max_uses=300, is_active=True, valid_from=now - timedelta(days=15), valid_until=now + timedelta(days=180)),
        ]
        session.add_all(coupons)
        print("Created 3 coupons")

        # 7. Create orders
        statuses = ["delivered", "delivered", "shipped", "shipped", "processing", "processing", "pending_payment", "cancelled"]
        for i, status in enumerate(statuses):
            buyer = buyers[i % len(buyers)]
            product = products[i % len(products)]
            qty = random.randint(1, 3)
            subtotal = product.price * qty
            shipping = Decimal("0") if subtotal >= 999 else Decimal("99")
            total = subtotal + shipping
            order = Order(
                id=uuid.uuid4(),
                order_number=f"ORD-2024{(i+1):04d}",
                buyer_id=buyer.id,
                status=status,
                payment_status="paid" if status in ["delivered", "shipped", "processing"] else "pending",
                shipping_address_json={"name": f"{buyer.first_name} {buyer.last_name}", "city": "Mumbai", "state": "Maharashtra", "pincode": "400001"},
                billing_address_json={"name": f"{buyer.first_name} {buyer.last_name}", "city": "Mumbai", "state": "Maharashtra", "pincode": "400001"},
                subtotal=subtotal, grand_total=total, shipping_total=shipping,
            )
            session.add(order)
            await session.flush()
            order_item = OrderItem(id=uuid.uuid4(), order_id=order.id, product_id=product.id, product_title=product.title, quantity=qty, unit_price=product.price, total_price=product.price * qty)
            session.add(order_item)
        print(f"Created {len(statuses)} orders")

        await session.commit()
        print("E-commerce sample data seeded successfully!")


if __name__ == "__main__":
    asyncio.run(seed_sample_data())
