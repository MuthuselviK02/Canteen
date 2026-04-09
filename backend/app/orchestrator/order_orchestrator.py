from sqlalchemy.orm import Session
from datetime import datetime
import logging

from app.services.queue_service import assign_queue_position
from app.services.order_service import create_order
from app.services.inventory_service import deduct_stock
from app.models.menu import MenuItem
from app.models.order_item import OrderItem
from app.ml.features import extract_features
from app.ml.model import predict_wait_time

logger = logging.getLogger(__name__)

def place_order(
    db: Session,
    user_id: int,
    items,
    available_time: int | None = None
):
    if not items:
        raise ValueError("Order must contain at least one item")

    try:
        queue_position = assign_queue_position(db)

        features = extract_features(
            queue_position=queue_position,
            total_items=len(items),
            total_quantity=sum(i.quantity for i in items),
            created_at=datetime.utcnow(),
        )

        ml_prediction = predict_wait_time(features)

        predicted_time = (
            ml_prediction
            if ml_prediction is not None
            else 15  # fallback to 15 minutes
        )

        validated_items = []
        total_amount = 0.0
        for item_data in items:
            menu_item = db.query(MenuItem).filter(MenuItem.id == item_data.menu_item_id).first()
            if not menu_item:
                raise ValueError(f"Menu item {item_data.menu_item_id} not found")
            if int(item_data.quantity) <= 0:
                raise ValueError("Item quantity must be greater than zero")

            validated_items.append((item_data, menu_item))
            total_amount += float(menu_item.price or 0) * int(item_data.quantity)

        # Create order first
        order = create_order(
            db,
            user_id=user_id,
            queue_position=queue_position,
            predicted_time=predicted_time
        )

        # Add order items
        for item_data, _menu_item in validated_items:
            order_item = OrderItem(
                order_id=order.id,
                menu_item_id=item_data.menu_item_id,
                quantity=item_data.quantity
            )
            db.add(order_item)

        order.total_amount = total_amount
        db.commit()
        db.refresh(order)

        # Deduct stock
        try:
            for item_data in items:
                try:
                    deduct_stock(db, item_data.menu_item_id, item_data.quantity)
                except Exception as stock_error:
                    logger.warning(f"Stock deduction failed for item {item_data.menu_item_id}: {stock_error}")
                    # Continue with order even if stock deduction fails
        except Exception as e:
            logger.warning(f"Stock deduction process failed: {e}")

        return order

    except Exception as e:
        logger.error(f"Error in place_order: {e}")
        db.rollback()
        # Fallback: create order without ML prediction
        try:
            if not items:
                raise ValueError("Order must contain at least one item")

            queue_position = assign_queue_position(db)
            validated_items = []
            total_amount = 0.0
            for item_data in items:
                menu_item = db.query(MenuItem).filter(MenuItem.id == item_data.menu_item_id).first()
                if not menu_item:
                    raise ValueError(f"Menu item {item_data.menu_item_id} not found")
                if int(item_data.quantity) <= 0:
                    raise ValueError("Item quantity must be greater than zero")

                validated_items.append((item_data, menu_item))
                total_amount += float(menu_item.price or 0) * int(item_data.quantity)

            order = create_order(
                db,
                user_id=user_id,
                queue_position=queue_position,
                predicted_time=15  # default fallback
            )
            
            # Add order items
            for item_data, _menu_item in validated_items:
                order_item = OrderItem(
                    order_id=order.id,
                    menu_item_id=item_data.menu_item_id,
                    quantity=item_data.quantity
                )
                db.add(order_item)
            
            order.total_amount = total_amount
            db.commit()
            db.refresh(order)
            
            # Deduct stock for fallback
            try:
                for item_data in items:
                    try:
                        deduct_stock(db, item_data.menu_item_id, item_data.quantity)
                    except Exception as stock_error:
                        logger.warning(f"Stock deduction failed for item {item_data.menu_item_id} in fallback: {stock_error}")
            except Exception as e:
                logger.warning(f"Stock deduction process failed in fallback: {e}")
            
            return order
        except Exception as fallback_error:
            logger.error(f"Fallback order creation also failed: {fallback_error}")
            db.rollback()
            raise e
