from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class ProductCreate(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    quantity: int = 0
    category: Optional[str] = None
    image_url: Optional[str] = None


class ProductOut(BaseModel):
    id: UUID
    title: str
    description: Optional[str]
    price: float
    quantity: int
    category: Optional[str]
    image_url: Optional[str]
    seller_id: UUID
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True