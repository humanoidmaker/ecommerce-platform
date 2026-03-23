from __future__ import annotations
import uuid
from pathlib import PurePosixPath

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
MAX_IMAGE_SIZE_MB = 10


def generate_storage_key(prefix: str, filename: str) -> str:
    uid = uuid.uuid4().hex[:12]
    safe = PurePosixPath(filename).name
    return f"{prefix}/{uid}/{safe}"


def sanitize_filename(filename: str) -> str:
    return PurePosixPath(filename).name.replace("\x00", "").strip()


def is_valid_image_type(mime: str) -> bool:
    return mime in ALLOWED_IMAGE_TYPES


def validate_file_size(size: int, max_mb: int = MAX_IMAGE_SIZE_MB) -> bool:
    return size <= max_mb * 1024 * 1024
