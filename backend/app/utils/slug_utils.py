"""Slug generation utilities."""
from __future__ import annotations
import re
import uuid


def generate_slug(text: str, max_length: int = 200) -> str:
    """Generate URL-safe slug from text."""
    slug = text.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[-\s]+", "-", slug)
    slug = slug.strip("-")
    return slug[:max_length]


def generate_unique_slug(text: str, max_length: int = 200) -> str:
    """Generate slug with a short unique suffix."""
    base = generate_slug(text, max_length - 9)
    suffix = uuid.uuid4().hex[:8]
    return f"{base}-{suffix}"


def is_valid_slug(slug: str) -> bool:
    """Check if string is a valid slug."""
    return bool(re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", slug))
