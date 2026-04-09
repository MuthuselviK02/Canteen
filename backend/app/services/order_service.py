from sqlalchemy.orm import Session
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.menu import MenuItem
from app.models.user import User
from app.services.order_time_service import OrderTimeService


def create_order(db: Session, user_id: int, queue_position: int, predicted_time: int):
    order = Order(
        user_id=user_id,
        queue_position=queue_position,
        predicted_wait_time=predicted_time,
        status="pending"
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


def get_user_orders_with_items(db: Session, user_id: int):
    orders = db.query(Order).filter(Order.user_id == user_id).all()
    
    # Attach menu item info and user info to each order
    for order in orders:
        # Get user info
        user = db.query(User).filter(User.id == order.user_id).first()
        if user:
            order.user = user
        
        # Get order items with menu details
        order_items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
        for item in order_items:
            # Get menu item details
            menu_item = db.query(MenuItem).filter(MenuItem.id == item.menu_item_id).first()
            if menu_item:
                item.menu_item = menu_item
        
        # Calculate dynamic wait time based on order items and queue
        order.predicted_wait_time = OrderTimeService.calculate_dynamic_wait_time(order, db)
    
    return orders


def get_order_with_items(db: Session, order_id: int, user_id: int):
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == user_id
    ).first()
    
    if order:
        # Get user info
        user = db.query(User).filter(User.id == order.user_id).first()
        if user:
            order.user = user
        
        # Attach menu item info
        order_items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
        for item in order_items:
            menu_item = db.query(MenuItem).filter(MenuItem.id == item.menu_item_id).first()
            if menu_item:
                item.menu_item = menu_item
        
        # Calculate dynamic wait time based on order items and queue
        order.predicted_wait_time = OrderTimeService.calculate_dynamic_wait_time(order, db)
    
    return order


def update_order_status(db: Session, order_id: int, status: str):
    """
    Update order status with proper timestamp tracking.
    """
    return OrderTimeService.update_order_status_with_time(order_id, status, db)


def get_order_time_summary(db: Session, order_id: int):
    """
    Get comprehensive time summary for an order.
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    if order:
        return OrderTimeService.get_order_time_summary(order)
    return None


def update_orders_queue(db: Session):
    """
    Update queue positions and recalculate wait times for all pending orders.
    """
    return OrderTimeService.auto_update_orders_queue(db)


def delete_order(db: Session, order_id: int) -> bool:
    """
    Delete an order and its associated order items.
    Returns True if successful, False otherwise.
    """
    try:
        # First delete all order items associated with this order
        order_items = db.query(OrderItem).filter(OrderItem.order_id == order_id).all()
        for item in order_items:
            db.delete(item)
        
        # Then delete the order itself
        order = db.query(Order).filter(Order.id == order_id).first()
        if order:
            db.delete(order)
            db.commit()
            return True
        else:
            return False
            
    except Exception as e:
        print(f"Error deleting order {order_id}: {e}")
        db.rollback()
        return False
