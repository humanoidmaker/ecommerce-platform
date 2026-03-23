from __future__ import annotations
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "E-Commerce Platform"
    debug: bool = False
    api_prefix: str = "/api/v1"
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:3001", "http://localhost:3002"]

    # Database
    database_url: str = "postgresql+asyncpg://ecommerce:ecommerce@localhost:5432/ecommerce"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # JWT
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # MinIO
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_secure: bool = False
    minio_bucket_products: str = "ecommerce-products"
    minio_bucket_sellers: str = "ecommerce-sellers"
    minio_bucket_invoices: str = "ecommerce-invoices"
    minio_bucket_misc: str = "ecommerce-misc"

    # Celery
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    # Email
    smtp_host: str = "localhost"
    smtp_port: int = 1025
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from_email: str = "noreply@ecommerce.local"
    smtp_use_tls: bool = False

    # Business rules
    default_commission_rate: float = 0.15  # 15%
    default_tax_rate: float = 0.08  # 8%
    free_shipping_threshold: float = 75.00
    max_images_per_product: int = 10
    max_variants_per_product: int = 50
    cart_expiry_hours: int = 72
    abandoned_cart_hours: int = 1
    review_reminder_days: int = 7
    trash_purge_days: int = 30

    # Rate limiting
    rate_limit_per_minute: int = 120

    model_config = {"env_prefix": "BAZAAR_", "env_file": ".env", "extra": "ignore"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
