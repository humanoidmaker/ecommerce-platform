"""Tests for slug generation."""
from app.utils.slug_utils import generate_slug, generate_unique_slug, is_valid_slug


def test_basic_slug():
    assert generate_slug("Hello World") == "hello-world"

def test_special_chars():
    assert generate_slug("Product #1 (New!)") == "product-1-new"

def test_max_length():
    assert len(generate_slug("a" * 300, 50)) <= 50

def test_unique_slug_has_suffix():
    slug = generate_unique_slug("Test Product")
    assert slug.startswith("test-product-")
    assert len(slug) > len("test-product")

def test_is_valid_slug():
    assert is_valid_slug("hello-world")
    assert is_valid_slug("product-123")
    assert not is_valid_slug("Hello World")
    assert not is_valid_slug("")
