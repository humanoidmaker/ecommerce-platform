from __future__ import annotations


def is_buyer(role: str) -> bool:
    return role in ("buyer", "admin", "superadmin")


def is_seller(role: str) -> bool:
    return role in ("seller", "admin", "superadmin")


def is_admin(role: str) -> bool:
    return role in ("admin", "superadmin")


def is_superadmin(role: str) -> bool:
    return role == "superadmin"
