"""Tests for role permissions."""
from app.utils.permissions import is_buyer, is_seller, is_admin, is_superadmin


def test_buyer_role():
    assert is_buyer("buyer")
    assert is_buyer("admin")
    assert not is_buyer("seller")

def test_seller_role():
    assert is_seller("seller")
    assert is_seller("admin")
    assert not is_seller("buyer")

def test_admin_role():
    assert is_admin("admin")
    assert is_admin("superadmin")
    assert not is_admin("buyer")
    assert not is_admin("seller")

def test_superadmin_only():
    assert is_superadmin("superadmin")
    assert not is_superadmin("admin")

def test_admin_has_buyer_access():
    assert is_buyer("admin")

def test_admin_has_seller_access():
    assert is_seller("admin")

def test_superadmin_has_all():
    assert is_buyer("superadmin")
    assert is_seller("superadmin")
    assert is_admin("superadmin")
    assert is_superadmin("superadmin")
