from datetime import datetime

from pydantic import BaseModel


class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = 1


class OrderCreate(BaseModel):
    items: list[OrderItemCreate]


class OrderItemOut(BaseModel):
    id: int
    product_id: int
    quantity: int
    price: float

    class Config:
        from_attributes = True


class OrderOut(BaseModel):
    id: int
    buyer_id: int
    status: str
    total_price: float
    created_at: datetime
    items: list[OrderItemOut] = []

    class Config:
        from_attributes = True