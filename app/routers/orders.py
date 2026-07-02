from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.order import Order, OrderItem, OrderStatus
from app.models.product import Product
from app.models.user import User
from app.schemas.order import OrderCreate, OrderOut
from app.services.auth import get_current_user

router = APIRouter(prefix="/api/orders", tags=["orders"])


@router.get("/", response_model=list[OrderOut])
def get_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(Order).filter(Order.buyer_id == current_user.id).all()


@router.get("/{order_id}", response_model=OrderOut)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    order = db.query(Order).filter(Order.id == order_id, Order.buyer_id == current_user.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.post("/", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
def create_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    order = Order(buyer_id=current_user.id, total_price=0.0)
    db.add(order)
    db.flush()

    total = 0.0
    for item_data in order_data.items:
        product = db.query(Product).filter(Product.id == item_data.product_id).first()
        if not product or not product.is_active:
            raise HTTPException(status_code=400, detail=f"Product {item_data.product_id} not available")
        if product.quantity < item_data.quantity:
            raise HTTPException(status_code=400, detail=f"Not enough stock for product {product.title}")

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
    db.commit()
    db.refresh(order)
    return order


@router.patch("/{order_id}/status", response_model=OrderOut)
def update_order_status(
    order_id: int,
    status: OrderStatus,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Buyer can cancel, seller can change other statuses
    if current_user.id == order.buyer_id:
        if status != OrderStatus.CANCELLED:
            raise HTTPException(status_code=403, detail="Buyer can only cancel orders")
    else:
        product_seller_ids = {item.product.seller_id for item in order.items}
        if current_user.id not in product_seller_ids:
            raise HTTPException(status_code=403, detail="Not your order to manage")

    order.status = status
    db.commit()
    db.refresh(order)
    return order