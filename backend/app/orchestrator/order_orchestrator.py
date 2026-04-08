from sqlalchemy.orm import Session
from datetime import datetime
import logging

from app.services.queue_service import assign_queue_position
from app.services.order_service import create_order
from app.services.inventory_service import deduct_stock
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

        # Create order first
        order = create_order(
            db,
            user_id=user_id,
            queue_position=queue_position,
            predicted_time=predicted_time
        )

        # Add order items
        for item_data in items:
            order_item = OrderItem(
                order_id=order.id,
                menu_item_id=item_data.menu_item_id,
                quantity=item_data.quantity
            )
            db.add(order_item)

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
        # Fallback: create order without ML prediction
        try:
            queue_position = assign_queue_position(db)
            order = create_order(
                db,
                user_id=user_id,
                queue_position=queue_position,
                predicted_time=15  # default fallback
            )
            
            # Add order items
            for item_data in items:
                order_item = OrderItem(
                    order_id=order.id,
                    menu_item_id=item_data.menu_item_id,
                    quantity=item_data.quantity
                )
                db.add(order_item)
            
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
            raise e
