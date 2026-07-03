"""
Pydantic-схемы для каталога: категории и товары.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class CategoryShort(BaseModel):
    """Краткая информация о категории (вложена в товар)."""
    id: UUID
    name: str
    slug: str

    class Config:
        from_attributes = True


class CategoryOut(BaseModel):
    """Категория с дочерними элементами для построения дерева."""
    id: UUID
    name: str
    slug: str
    image_url: Optional[str] = None
    children: Optional[list["CategoryOut"]] = None

    class Config:
        from_attributes = True


class ProductShort(BaseModel):
    """Краткое представление товара в списке."""
    id: UUID
    name: str
    price: float
    quantity: int
    image_urls: list = []
    category: Optional[CategoryShort] = None

    class Config:
        from_attributes = True


class ProductDetail(BaseModel):
    """Полная информация о товаре."""
    id: UUID
    name: str
    description: str = ""
    price: float
    quantity: int
    image_urls: list = []
    attributes: dict = {}
    category: Optional[CategoryShort] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    """Ответ списка товаров с пагинацией."""
    items: list[ProductShort]
    total: int
    page: int
    limit: int
