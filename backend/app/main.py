from __future__ import annotations
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.middleware.rate_limiter import RateLimitMiddleware
from app.middleware.request_logger import RequestLoggerMiddleware

settings = get_settings()
logging.basicConfig(level=logging.DEBUG if settings.debug else logging.INFO, format="%(asctime)s %(levelname)-8s %(name)s: %(message)s")

app = FastAPI(title=settings.app_name, version="1.0.0", docs_url="/api/docs" if settings.debug else None)

app.add_middleware(RequestLoggerMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


@app.get("/health")
async def health():
    return {"status": "ok", "service": settings.app_name}


# Auth routes
from app.api.auth import router as auth_router  # noqa: E402
app.include_router(auth_router, prefix=settings.api_prefix)

# Buyer routes
from app.api.buyer.catalog import router as catalog_router  # noqa: E402
from app.api.buyer.products import router as products_router  # noqa: E402
from app.api.buyer.search import router as search_router  # noqa: E402
from app.api.buyer.cart import router as cart_router  # noqa: E402
from app.api.buyer.checkout import router as checkout_router  # noqa: E402
from app.api.buyer.orders import router as orders_router  # noqa: E402
from app.api.buyer.reviews import router as reviews_router  # noqa: E402
from app.api.buyer.wishlist import router as wishlist_router  # noqa: E402
from app.api.buyer.tracking import router as tracking_router  # noqa: E402
from app.api.buyer.addresses import router as addresses_router  # noqa: E402
for r in [catalog_router, products_router, search_router, cart_router, checkout_router, orders_router, reviews_router, wishlist_router, tracking_router, addresses_router]:
    app.include_router(r, prefix=settings.api_prefix)

# Seller routes
from app.api.seller.store import router as seller_store_router  # noqa: E402
from app.api.seller.products import router as seller_products_router  # noqa: E402
from app.api.seller.orders import router as seller_orders_router  # noqa: E402
from app.api.seller.analytics import router as seller_analytics_router  # noqa: E402
for r in [seller_store_router, seller_products_router, seller_orders_router, seller_analytics_router]:
    app.include_router(r, prefix=settings.api_prefix)

# Admin routes will be added in phase 5/6


@app.on_event("startup")
async def on_startup():
    logging.getLogger("ecommerce").info("E-Commerce Platform API starting up")
    try:
        from app.utils.minio_client import ensure_buckets
        ensure_buckets()
    except Exception as e:
        logging.getLogger("ecommerce").warning("MinIO init failed: %s", e)


@app.on_event("shutdown")
async def on_shutdown():
    from app.database import engine
    await engine.dispose()
