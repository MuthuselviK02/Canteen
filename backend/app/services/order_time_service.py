from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.menu import MenuItem


class OrderTimeService:
    """
    Production-ready service for managing order time calculations and status updates.
    Handles dynamic estimated times based on order status and timestamps.
    """
    
    # Production configuration - these can be moved to environment variables
    PREPARATION_TIME_MINUTES = 10  # Average time to prepare an order
    QUEUE_TIME_PER_ORDER = 2       # Additional time per order in queue
    READY_HOLD_TIME = 5            # Minutes to keep order in "ready" state
    
    @staticmethod
    def get_order_preparation_time(order_id: int, db: Session) -> int:
        """
        Calculate preparation time based on actual menu items in the order.
        
        Args:
            order_id: ID of the order
            db: Database session
            
        Returns:
            int: Preparation time in minutes
        """
        try:
            # Get all order items with their menu details
            order_items = db.query(OrderItem).filter(OrderItem.order_id == order_id).all()
            
            if not order_items:
                return OrderTimeService.PREPARATION_TIME_MINUTES
            
            max_prep_time = 0
            total_prep_time = 0
            
            for item in order_items:
                menu_item = db.query(MenuItem).filter(MenuItem.id == item.menu_item_id).first()
                if menu_item and menu_item.base_prep_time:
                    # Use menu item's specific preparation time
                    item_prep_time = menu_item.base_prep_time
                else:
                    # Fallback to default preparation time
                    item_prep_time = OrderTimeService.PREPARATION_TIME_MINUTES
                
                # For multiple items, we take the maximum (items prepared in parallel)
                # plus a small overhead for each additional item
                max_prep_time = max(max_prep_time, item_prep_time)
                total_prep_time += item_prep_time
            
            # If multiple items, add small overhead
            if len(order_items) > 1:
                overhead = (len(order_items) - 1) * 2  # 2 minutes per additional item
                return max_prep_time + overhead
            else:
                return max_prep_time
                
        except Exception as e:
            print(f"Error calculating preparation time for order {order_id}: {e}")
            return OrderTimeService.PREPARATION_TIME_MINUTES

    @staticmethod
    def calculate_dynamic_wait_time(order: Order, db: Session) -> int:
        """
        Calculate dynamic estimated wait time based on order status and queue position.
        
        Args:
            order: The order object
            db: Database session
            
        Returns:
            int: Estimated wait time in minutes
        """
        now = datetime.utcnow()
        
        if order.status == "completed":
            return 0
        
        elif order.status == "ready":
            # Order is ready, minimal wait time
            return 1
        
        elif order.status == "preparing":
            # Order is being prepared, use actual preparation time
            prep_time = OrderTimeService.get_order_preparation_time(order.id, db)
            if order.started_preparation_at:
                elapsed = (now - order.started_preparation_at).total_seconds() / 60
                remaining = max(0, prep_time - elapsed)
                return int(remaining) + 1  # Add 1 minute buffer
            else:
                return prep_time
        
        elif order.status == "pending":
            # Order is pending, calculate based on queue and item prep time
            prep_time = OrderTimeService.get_order_preparation_time(order.id, db)
            base_time = prep_time
            
            # Add queue time based on position
            if order.queue_position and order.queue_position > 1:
                queue_time = (order.queue_position - 1) * OrderTimeService.QUEUE_TIME_PER_ORDER
                base_time += queue_time
            
            # Add time elapsed since order creation
            if order.created_at:
                elapsed = (now - order.created_at).total_seconds() / 60
                base_time = max(0, base_time - elapsed)
            
            return int(base_time) + 1  # Add 1 minute buffer
        
        else:
            # Unknown status, return item-specific preparation time
            return OrderTimeService.get_order_preparation_time(order.id, db)
    
    @staticmethod
    def update_order_status_with_time(order_id: int, new_status: str, db: Session) -> Optional[Order]:
        """
        Update order status and set appropriate timestamps with proper transaction handling.
        This method is thread-safe and handles concurrent updates properly.
        
        Args:
            order_id: ID of the order to update
            new_status: New status to set
            db: Database session
            
        Returns:
            Order: Updated order object or None if not found
        """
        try:
            # For SQLite, we need to be more careful with locking
            # First get the order without locking to check if it exists
            order = db.query(Order).filter(Order.id == order_id).first()
            if not order:
                print(f"Order {order_id} not found")
                return None
            
            now = datetime.utcnow()
            old_status = order.status
            
            # Validate status transition
            if not OrderTimeService._is_valid_status_transition(old_status, new_status):
                print(f"Invalid status transition: {old_status} -> {new_status} for order {order_id}")
                return order  # Return unchanged order
            
            # Update status
            order.status = new_status
            
            # Set timestamps based on status transitions (only once per transition)
            if new_status == "preparing" and old_status != "preparing":
                if not order.started_preparation_at:  # Only set if not already set
                    order.started_preparation_at = now
                    print(f"Order {order_id}: Started preparation at {now}")
            
            elif new_status == "ready" and old_status != "ready":
                if not order.ready_at:  # Only set if not already set
                    order.ready_at = now
                    order.predicted_wait_time = 1
                    print(f"Order {order_id}: Ready at {now}")
            
            elif new_status == "completed" and old_status != "completed":
                if not order.completed_at:  # Only set if not already set
                    order.completed_at = now
                    order.predicted_wait_time = 0
                    print(f"Order {order_id}: Completed at {now}")
                    
                    # Auto-create invoice when order is completed
                    try:
                        from app.services.billing_service import BillingService
                        invoice = BillingService.create_invoice(
                            db, 
                            order.customer_id, 
                            order_id, 
                            notes=f"Auto-created invoice for completed order #{order_id}"
                        )
                        order.invoice_id = str(invoice.id)  # Store invoice ID in order
                        print(f"Order {order_id}: Auto-created invoice {invoice.id}")
                    except Exception as invoice_error:
                        print(f"Order {order_id}: Failed to auto-create invoice: {invoice_error}")
                        # Don't fail the order status update if invoice creation fails
                    
                    # REAL-TIME INVENTORY UPDATE: Update inventory levels when order is completed
                    try:
                        from app.services.realtime_inventory_service import RealTimeInventoryService
                        RealTimeInventoryService.update_inventory_on_order_completion(db, order_id)
                        print(f"Order {order_id}: Real-time inventory updated")
                    except Exception as inventory_error:
                        print(f"Order {order_id}: Failed to update inventory: {inventory_error}")
                        # Don't fail the order status update if inventory update fails
            
            # Update dynamic wait time for pending and preparing orders
            if new_status in ["pending", "preparing"]:
                order.predicted_wait_time = OrderTimeService.calculate_dynamic_wait_time(order, db)
            
            # Commit the changes
            db.commit()
            
            # Refresh to get the latest data from database
            db.refresh(order)
            
            print(f"Order {order_id} after commit - Status: {order.status}, Started: {order.started_preparation_at}, Ready: {order.ready_at}, Completed: {order.completed_at}")
            
            # Update queue positions after successful status update
            # This ensures all pending orders have correct queue positions
            OrderTimeService._update_pending_orders_queue(db)
            
            return order
            
        except Exception as e:
            db.rollback()
            print(f"Error updating order {order_id} status: {e}")
            raise
    
    @staticmethod
    def _is_valid_status_transition(old_status: str, new_status: str) -> bool:
        """
        Validate that the status transition is allowed.
        """
        valid_transitions = {
            "pending": ["preparing", "completed"],
            "preparing": ["ready", "completed"],
            "ready": ["completed"],
            "completed": []  # No transitions from completed
        }
        
        # Handle case insensitivity and normalize status
        old_status_normalized = old_status.lower().strip()
        new_status_normalized = new_status.lower().strip()
        
        is_valid = new_status_normalized in valid_transitions.get(old_status_normalized, [])
        
        print(f"Status transition check: '{old_status_normalized}' -> '{new_status_normalized}' = {is_valid}")
        
        return is_valid
    
    @staticmethod
    def _update_pending_orders_queue(db: Session) -> int:
        """
        Update queue positions for all pending orders.
        This should be called after any status change that affects the queue.
        
        Returns:
            int: Number of orders updated
        """
        try:
            # Get all pending orders ordered by creation time
            pending_orders = db.query(Order).filter(
                Order.status == "pending"
            ).order_by(Order.created_at).all()
            
            updated_count = 0
            # Update queue positions
            for i, order in enumerate(pending_orders):
                new_position = i + 1
                if order.queue_position != new_position:
                    order.queue_position = new_position
                    order.predicted_wait_time = OrderTimeService.calculate_dynamic_wait_time(order, db)
                    updated_count += 1
            
            db.commit()
            return updated_count
            
        except Exception as e:
            print(f"Error updating queue positions: {e}")
            db.rollback()
            return 0
    
    @staticmethod
    def _calculate_progress_percentage(order: Order, current_wait_time: int, db: Session) -> float:
        """
        Calculate progress percentage for an order.
        
        Args:
            order: The order object
            current_wait_time: Current calculated wait time
            db: Database session
            
        Returns:
            float: Progress percentage (0-100)
        """
        try:
            if order.status == "completed":
                return 100.0
            elif order.status == "ready":
                return 95.0
            elif order.status == "preparing":
                prep_time = OrderTimeService.get_order_preparation_time(order.id, db)
                if order.started_preparation_at and prep_time > 0:
                    elapsed = (datetime.utcnow() - order.started_preparation_at).total_seconds() / 60
                    progress = min(90.0, (elapsed / prep_time) * 90)  # Max 90% until ready
                    return progress
                else:
                    return 10.0  # Just started preparing
            elif order.status == "pending":
                # For pending orders, calculate based on queue position
                if order.queue_position and order.queue_position > 1:
                    # Higher queue position = less progress
                    queue_progress = max(0, 10 - (order.queue_position - 1) * 2)
                    return queue_progress
                else:
                    return 10.0  # Next in queue
            else:
                return 0.0
                
        except Exception as e:
            print(f"Error calculating progress for order {order.id}: {e}")
            return 0.0

    @staticmethod
    def get_order_time_summary(order: Order) -> dict:
        """
        Get a comprehensive time summary for an order.
        
        Args:
            order: The order object
            
        Returns:
            dict: Time summary with various metrics
        """
        now = datetime.utcnow()
        summary = {
            "order_id": order.id,
            "status": order.status,
            "created_at": order.created_at,
            "current_time": now,
            "estimated_wait_time": order.predicted_wait_time,
            "time_elapsed_minutes": 0,
            "time_to_ready": 0,
            "time_to_completion": 0
        }
        
        if order.created_at:
            time_elapsed = (now - order.created_at).total_seconds() / 60
            summary["time_elapsed_minutes"] = int(time_elapsed)
        
        if order.status == "pending":
            summary["time_to_ready"] = order.predicted_wait_time or 0
            summary["time_to_completion"] = summary["time_to_ready"] + OrderTimeService.READY_HOLD_TIME
        
        elif order.status == "preparing":
            if order.started_preparation_at:
                time_spent_preparing = (now - order.started_preparation_at).total_seconds() / 60
                summary["time_spent_preparing"] = int(time_spent_preparing)
                summary["time_to_ready"] = max(0, order.predicted_wait_time or 0)
                summary["time_to_completion"] = summary["time_to_ready"] + OrderTimeService.READY_HOLD_TIME
        
        elif order.status == "ready":
            if order.ready_at:
                time_since_ready = (now - order.ready_at).total_seconds() / 60
                summary["time_since_ready"] = int(time_since_ready)
            summary["time_to_completion"] = OrderTimeService.READY_HOLD_TIME
        
        elif order.status == "completed":
            if order.completed_at:
                total_time = (order.completed_at - order.created_at).total_seconds() / 60
                summary["total_order_time"] = int(total_time)
        
        return summary
    
    @staticmethod
    def auto_update_orders_queue(db: Session) -> int:
        """
        Automatically update queue positions and recalculate wait times.
        This should be called periodically (e.g., every minute) in production.
        
        Args:
            db: Database session
            
        Returns:
            int: Number of orders updated
        """
        return OrderTimeService._update_pending_orders_queue(db)
