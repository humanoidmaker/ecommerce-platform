from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Sequence
from fastapi import Query
from pydantic import BaseModel


@dataclass
class PaginationParams:
    page: int = 1
    page_size: int = 20

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size


def get_pagination(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100)) -> PaginationParams:
    return PaginationParams(page=page, page_size=page_size)


class PaginatedResponse(BaseModel):
    items: list[Any]
    total: int
    page: int
    page_size: int
    total_pages: int

    @classmethod
    def create(cls, items: Sequence[Any], total: int, params: PaginationParams) -> PaginatedResponse:
        return cls(items=list(items), total=total, page=params.page, page_size=params.page_size, total_pages=max(1, (total + params.page_size - 1) // params.page_size))
