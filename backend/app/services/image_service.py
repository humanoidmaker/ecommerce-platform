"""Product image processing — resize, thumbnail, upload to MinIO."""
from __future__ import annotations
import io
from typing import Optional
from app.config import get_settings
from app.utils.minio_client import upload_bytes
from app.utils.file_utils import generate_storage_key

# Image sizes: (name, max_width, max_height, quality)
IMAGE_SIZES = {
    "main": (1200, 1200, 85),
    "medium": (600, 600, 80),
    "thumbnail": (200, 200, 75),
}


def process_product_image(data: bytes, filename: str) -> dict:
    """Process uploaded image: resize to standard sizes, return keys/urls."""
    try:
        from PIL import Image as PILImage
    except ImportError:
        # Fallback: just upload original
        return _upload_original(data, filename)

    img = PILImage.open(io.BytesIO(data))
    if img.mode in ("RGBA", "P"):
        # Convert to RGB with white background
        bg = PILImage.new("RGB", img.size, (255, 255, 255))
        if img.mode == "RGBA":
            bg.paste(img, mask=img.split()[3])
        else:
            bg.paste(img)
        img = bg

    original_width, original_height = img.size
    settings = get_settings()
    results = {}

    for size_name, (max_w, max_h, quality) in IMAGE_SIZES.items():
        resized = _resize_contain(img, max_w, max_h)
        buf = io.BytesIO()
        resized.save(buf, format="JPEG", quality=quality, optimize=True)
        buf.seek(0)

        key = generate_storage_key(f"products/{size_name}", filename.rsplit(".", 1)[0] + ".jpg")
        upload_bytes(settings.minio_bucket_products, key, buf.getvalue(), "image/jpeg")

        results[size_name] = {
            "key": key,
            "width": resized.width,
            "height": resized.height,
        }

    return {
        "image_key": results["main"]["key"],
        "thumbnail_key": results["thumbnail"]["key"],
        "width": original_width,
        "height": original_height,
        "sizes": results,
    }


def _resize_contain(img, max_w: int, max_h: int):
    """Resize image to fit within max dimensions, maintaining aspect ratio."""
    from PIL import Image as PILImage
    ratio = min(max_w / img.width, max_h / img.height)
    if ratio >= 1:
        return img  # Already fits
    new_w = int(img.width * ratio)
    new_h = int(img.height * ratio)
    return img.resize((new_w, new_h), PILImage.LANCZOS)


def _upload_original(data: bytes, filename: str) -> dict:
    """Upload without processing (fallback when Pillow unavailable)."""
    settings = get_settings()
    key = generate_storage_key("products/original", filename)
    upload_bytes(settings.minio_bucket_products, key, data)
    return {"image_key": key, "thumbnail_key": key, "width": 0, "height": 0, "sizes": {}}
