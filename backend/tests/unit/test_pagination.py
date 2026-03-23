from app.utils.pagination import PaginationParams, PaginatedResponse


def test_offset_page_1():
    p = PaginationParams(page=1, page_size=20)
    assert p.offset == 0

def test_offset_page_3():
    p = PaginationParams(page=3, page_size=10)
    assert p.offset == 20

def test_paginated_response():
    r = PaginatedResponse.create(["a", "b"], total=50, params=PaginationParams(page=1, page_size=20))
    assert r.total == 50 and r.total_pages == 3

def test_single_page():
    r = PaginatedResponse.create(["a"], total=1, params=PaginationParams(page=1, page_size=20))
    assert r.total_pages == 1

def test_zero_total():
    r = PaginatedResponse.create([], total=0, params=PaginationParams(page=1, page_size=20))
    assert r.total_pages == 1

def test_exact_division():
    r = PaginatedResponse.create([], total=40, params=PaginationParams(page=1, page_size=20))
    assert r.total_pages == 2
