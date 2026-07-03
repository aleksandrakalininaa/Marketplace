import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.order import Order, OrderItem, OrderStatus
from app.models.product import Product
from app.models.user import User
from app.schemas.order import OrderCreate, OrderOut
from app.services.auth import get_current_user

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("/", response_model=list[OrderOut])
async def get_orders(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Order)
        .where(Order.buyer_id == current_user.id)
        .options(selectinload(Order.items))
    )
    return result.scalars().all()


@router.get("/{order_id}", response_model=OrderOut)
async def get_order(
    order_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Order)
        .where(Order.id == order_id, Order.buyer_id == current_user.id)
        .options(selectinload(Order.items))
    )
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.post("/", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    order = Order(buyer_id=current_user.id, total_price=0.0)
    db.add(order)
    await db.flush()

    total = 0.0
    for item_data in order_data.items:
        result = await db.execute(
            select(Product).where(Product.id == item_data.product_id)
        )
        product = result.scalar_one_or_none()
        if not product or not product.is_active:
            raise HTTPException(
                status_code=400, detail=f"Product {item_data.product_id} not available"
            )
        if product.quantity < item_data.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Not enough stock for product {product.title}",
            )

        product.quantity -= item_data.quantity
        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=item_data.quantity,
            price=product.price,
        )
        db.add(order_item)
        total += product.price * item_data.quantity

    order.total_price = total
    await db.flush()
    await db.refresh(order)
    return order


@router.patch("/{order_id}/status", response_model=OrderOut)
async def update_order_status(
    order_id: uuid.UUID,
    status_value: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Order)
        .where(Order.id == order_id)
        .options(selectinload(Order.items).selectinload(OrderItem.product))
    )
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if current_user.id == order.buyer_id:
        if status_value != OrderStatus.CANCELLED.value:
            raise HTTPException(
                status_code=403, detail="Buyer can only cancel orders"
            )
    else:
        product_seller_ids = {item.product.seller_id for item in order.items}
        if current_user.id not in product_seller_ids:
            raise HTTPException(status_code=403, detail="Not your order to manage")

    order.status = status_value
    await db.flush()
    await db.refresh(order)
    return order