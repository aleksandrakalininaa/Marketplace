from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ProductCreate(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    quantity: int = 0
    category: Optional[str] = None
    image_url: Optional[str] = None


class ProductOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    price: float
    quantity: int
    category: Optional[str]
    image_url: Optional[str]
    seller_id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True