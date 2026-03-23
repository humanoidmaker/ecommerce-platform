from __future__ import annotations
import io
from datetime import timedelta
from minio import Minio
from app.config import get_settings

settings = get_settings()
_client: Minio | None = None


def get_minio_client() -> Minio:
    global _client
    if _client is None:
        _client = Minio(endpoint=settings.minio_endpoint, access_key=settings.minio_access_key, secret_key=settings.minio_secret_key, secure=settings.minio_secure)
    return _client


def ensure_buckets() -> None:
    client = get_minio_client()
    for bucket in [settings.minio_bucket_products, settings.minio_bucket_sellers, settings.minio_bucket_invoices, settings.minio_bucket_misc]:
        if not client.bucket_exists(bucket):
            client.make_bucket(bucket)


def upload_bytes(bucket: str, key: str, data: bytes, content_type: str = "application/octet-stream") -> str:
    client = get_minio_client()
    client.put_object(bucket, key, io.BytesIO(data), len(data), content_type=content_type)
    return key


def download_bytes(bucket: str, key: str) -> bytes:
    client = get_minio_client()
    resp = client.get_object(bucket, key)
    try:
        return resp.read()
    finally:
        resp.close()
        resp.release_conn()


def get_presigned_url(bucket: str, key: str, hours: int = 1) -> str:
    return get_minio_client().presigned_get_object(bucket, key, expires=timedelta(hours=hours))


def delete_object(bucket: str, key: str) -> None:
    get_minio_client().remove_object(bucket, key)
