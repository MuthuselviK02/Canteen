"""
Real-time Inventory Update Service

This service automatically updates inventory levels when orders are completed,
ensuring the inventory dashboard always reflects current stock levels.
"""

from sqlalchemy.orm import Session
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.menu import MenuItem
from app.models.inventory import InventoryLog, InventoryStockUpdate
from datetime import datetime
from typing import Dict, List


class RealTimeInventoryService:
    
    @staticmethod
    def update_inventory_on_order_completion(db: Session, order_id: int):
        """
        Automatically update inventory levels when an order is marked as completed.
        This ensures real-time inventory tracking.
        
        Args:
            db: Database session
            order_id: ID of the completed order
        """
        try:
            # Get the completed order
            order = db.query(Order).filter(
                Order.id == order_id,
                Order.status == 'completed',
                Order.completed_at.isnot(None)
            ).first()
            
            if not order:
                print(f"Order {order_id} not found or not completed")
                return
            
            print(f"Updating inventory for completed order {order_id}")
            
            # Get all items in this order
            order_items = db.query(OrderItem).filter(OrderItem.order_id == order_id).all()
            
            for order_item in order_items:
                # Update the menu item's present stock
                menu_item = db.query(MenuItem).filter(MenuItem.id == order_item.menu_item_id).first()
                if menu_item:
                    # Calculate new stock level
                    current_stock = int(getattr(menu_item, 'present_stocks', 0) or 0)
                    quantity_consumed = int(order_item.quantity)
                    new_stock = max(0, current_stock - quantity_consumed)
                    
                    # Update the stock
                    menu_item.present_stocks = new_stock
                    
                    # Create inventory log
                    inventory_log = InventoryLog(
                        menu_item_id=menu_item.id,
                        quantity_used=quantity_consumed
                    )
                    db.add(inventory_log)
                    
                    # Create stock update record
                    stock_update = InventoryStockUpdate(
                        menu_item_id=menu_item.id,
                        previous_stock=current_stock,
                        quantity_delta=-quantity_consumed,  # Negative because stock decreased
                        new_stock=new_stock,
                        reason='order_completion',
                        order_id=order_id,  # Link to the order that caused this update
                        created_at=datetime.utcnow()
                    )
                    db.add(stock_update)
                    
                    print(f"Updated {menu_item.name}: {current_stock} -> {new_stock} (consumed {quantity_consumed})")
            
            # Commit all changes
            db.commit()
            print(f"Successfully updated inventory for order {order_id}")
            
        except Exception as e:
            db.rollback()
            print(f"Error updating inventory for order {order_id}: {e}")
            raise
    
    @staticmethod
    def bulk_update_inventory_for_completed_orders(db: Session):
        """
        Update inventory for all completed orders that haven't been processed yet.
        This can be used to sync inventory if it gets out of sync.
        """
        try:
            # Find completed orders that don't have corresponding inventory updates
            completed_orders_without_updates = db.query(Order).filter(
                Order.status == 'completed',
                Order.completed_at.isnot(None)
            ).outerjoin(InventoryStockUpdate, Order.id == InventoryStockUpdate.order_id)\
             .filter(InventoryStockUpdate.order_id.is_(None)).all()
            
            print(f"Found {len(completed_orders_without_updates)} completed orders without inventory updates")
            
            for order in completed_orders_without_updates:
                RealTimeInventoryService.update_inventory_on_order_completion(db, order.id)
            
            print("Bulk inventory update completed")
            
        except Exception as e:
            print(f"Error in bulk inventory update: {e}")
            raise
    
    @staticmethod
    def get_current_inventory_status(db: Session) -> Dict:
        """
        Get current inventory status for all menu items.
        """
        menu_items = db.query(MenuItem).all()
        inventory_status = {}
        
        for item in menu_items:
            inventory_status[item.id] = {
                'name': item.name,
                'category': item.category,
                'present_stock': int(getattr(item, 'present_stocks', 0) or 0),
                'last_updated': datetime.utcnow()
            }
        
        return inventory_status
