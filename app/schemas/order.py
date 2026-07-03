from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class OrderItemCreate(BaseModel):
    product_id: UUID
    quantity: int = 1


class OrderCreate(BaseModel):
    items: list[OrderItemCreate]


class OrderItemOut(BaseModel):
    id: UUID
    product_id: UUID
    quantity: int
    price: float

    class Config:
        from_attributes = True


class OrderOut(BaseModel):
    id: UUID
    buyer_id: UUID
    status: str
    total_price: float
    created_at: datetime
    items: list[OrderItemOut] = []

    class Config:
        from_attributes = True