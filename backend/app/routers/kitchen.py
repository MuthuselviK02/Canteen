from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.core.dependencies import staff_only
from app.models.order import Order
from app.models.user import User
from app.services.order_service import get_user_orders_with_items
from app.schemas.order import OrderResponse

router = APIRouter(prefix="/api/kitchen", tags=["Kitchen"])


@router.patch("/orders/{order_id}", response_model=OrderResponse)
def update_order_status(
    order_id: int,
    status: str,
    db: Session = Depends(get_db),
    staff=Depends(staff_only),
):
    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order.status = status
    db.commit()
    db.refresh(order)

    return order


@router.get("/orders", response_model=list[OrderResponse])
def list_orders(
    db: Session = Depends(get_db),
    staff=Depends(staff_only),
):
    """
    Get ALL orders from ALL users for kitchen dashboard.
    Includes user information and order items with menu details.
    """
    from app.models.order_item import OrderItem
    
    orders = db.query(Order).all()
    
    # Attach user info and order items for each order
    for order in orders:
        # Get user information
        user = db.query(User).filter(User.id == order.user_id).first()
        if user:
            order.user = user
        
        # Get order items with menu details
        order_items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
        for item in order_items:
            # Get menu item details
            from app.models.menu import MenuItem
            menu_item = db.query(MenuItem).filter(MenuItem.id == item.menu_item_id).first()
            if menu_item:
                item.menu_item = menu_item
    
    return orders
