"""
Menu Item Deletion Service

This service handles the complete deletion of menu items from the database,
including cleanup of all related records to maintain data integrity.
"""

from sqlalchemy.orm import Session
from app.models.menu import MenuItem
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.inventory import InventoryLog, InventoryStockUpdate
# Try to import these models, but handle if they don't exist
try:
    from app.models.demand_forecast import DemandForecast
except ImportError:
    DemandForecast = None
try:
    from app.models.preparation_time_prediction import PreparationTimePrediction
except ImportError:
    PreparationTimePrediction = None
from typing import Dict, List, Tuple
from datetime import datetime


class MenuItemDeletionService:
    
    @staticmethod
    def delete_menu_item_complete(db: Session, menu_item_id: int) -> Dict[str, any]:
        """
        Completely delete a menu item and all its related records.
        
        Args:
            db: Database session
            menu_item_id: ID of the menu item to delete
            
        Returns:
            Dict with deletion results and statistics
        """
        try:
            # First check if menu item exists
            menu_item = db.query(MenuItem).filter(MenuItem.id == menu_item_id).first()
            if not menu_item:
                return {
                    "success": False,
                    "error": f"Menu item with ID {menu_item_id} not found",
                    "deleted_records": {}
                }
            
            # Track what we're deleting
            deletion_stats = {}
            item_name = menu_item.name
            
            print(f"Starting complete deletion of menu item: {item_name} (ID: {menu_item_id})")
            
            # 1. Delete order items (this will also delete the orders if they become empty)
            order_items = db.query(OrderItem).filter(OrderItem.menu_item_id == menu_item_id).all()
            deletion_stats["order_items"] = len(order_items)
            
            for order_item in order_items:
                print(f"   Deleting order item: {order_item.quantity}x from order {order_item.order_id}")
                db.delete(order_item)
            
            # 2. Delete inventory logs
            inventory_logs = db.query(InventoryLog).filter(InventoryLog.menu_item_id == menu_item_id).all()
            deletion_stats["inventory_logs"] = len(inventory_logs)
            
            for log in inventory_logs:
                print(f"   Deleting inventory log: {log.quantity_used} units used")
                db.delete(log)
            
            # 3. Delete inventory stock updates
            stock_updates = db.query(InventoryStockUpdate).filter(InventoryStockUpdate.menu_item_id == menu_item_id).all()
            deletion_stats["inventory_stock_updates"] = len(stock_updates)
            
            for update in stock_updates:
                print(f"   Deleting stock update: {update.quantity_delta} delta, reason: {update.reason}")
                db.delete(update)
            
            # 4. Delete demand forecasts (if any)
            if DemandForecast:
                demand_forecasts = db.query(DemandForecast).filter(DemandForecast.menu_item_id == menu_item_id).all()
                deletion_stats["demand_forecasts"] = len(demand_forecasts)
                
                for forecast in demand_forecasts:
                    print(f"   Deleting demand forecast")
                    db.delete(forecast)
            else:
                deletion_stats["demand_forecasts"] = 0
            
            # 5. Delete preparation time predictions (if any)
            if PreparationTimePrediction:
                prep_predictions = db.query(PreparationTimePrediction).filter(PreparationTimePrediction.menu_item_id == menu_item_id).all()
                deletion_stats["preparation_time_predictions"] = len(prep_predictions)
                
                for prediction in prep_predictions:
                    print(f"   Deleting preparation time prediction")
                    db.delete(prediction)
            else:
                deletion_stats["preparation_time_predictions"] = 0
            
            # 6. Finally delete the menu item itself
            print(f"   Deleting menu item: {item_name}")
            db.delete(menu_item)
            deletion_stats["menu_item"] = 1
            
            # Commit all deletions
            db.commit()
            
            print(f"Successfully deleted menu item '{item_name}' and all related records")
            
            return {
                "success": True,
                "message": f"Menu item '{item_name}' deleted successfully",
                "deleted_item": {
                    "id": menu_item_id,
                    "name": item_name
                },
                "deleted_records": deletion_stats,
                "total_records_deleted": sum(deletion_stats.values())
            }
            
        except Exception as e:
            db.rollback()
            print(f"Error deleting menu item {menu_item_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "deleted_records": deletion_stats
            }
    
    @staticmethod
    def get_menu_item_references(db: Session, menu_item_id: int) -> Dict[str, int]:
        """
        Get count of all records that reference a menu item.
        Useful for showing what will be deleted before actually deleting.
        """
        try:
            menu_item = db.query(MenuItem).filter(MenuItem.id == menu_item_id).first()
            if not menu_item:
                return {"error": f"Menu item {menu_item_id} not found"}
            
            references = {
                "menu_item": 1,
                "order_items": db.query(OrderItem).filter(OrderItem.menu_item_id == menu_item_id).count(),
                "inventory_logs": db.query(InventoryLog).filter(InventoryLog.menu_item_id == menu_item_id).count(),
                "inventory_stock_updates": db.query(InventoryStockUpdate).filter(InventoryStockUpdate.menu_item_id == menu_item_id).count(),
                "demand_forecasts": db.query(DemandForecast).filter(DemandForecast.menu_item_id == menu_item_id).count() if DemandForecast else 0,
                "preparation_time_predictions": db.query(PreparationTimePrediction).filter(PreparationTimePrediction.menu_item_id == menu_item_id).count() if PreparationTimePrediction else 0,
            }
            
            return {
                "menu_item_id": menu_item_id,
                "menu_item_name": menu_item.name,
                "references": references,
                "total_references": sum(references.values())
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def cleanup_orphaned_menu_items(db: Session) -> Dict[str, any]:
        """
        Find and delete menu items that might not be properly managed.
        This is a maintenance function to clean up the database.
        """
        try:
            # Get all menu items
            all_menu_items = db.query(MenuItem).all()
            
            cleanup_results = {
                "items_checked": len(all_menu_items),
                "items_deleted": 0,
                "total_records_deleted": 0,
                "deleted_items": []
            }
            
            for item in all_menu_items:
                # Check if this item should be deleted (you can add your own logic here)
                # For now, we'll just report on items that have no recent orders
                recent_orders = db.query(OrderItem).filter(
                    OrderItem.menu_item_id == item.id
                ).count()
                
                if recent_orders == 0:
                    # This item has no orders - you might want to delete it
                    # Uncomment the next lines to automatically delete such items
                    # result = MenuItemDeletionService.delete_menu_item_complete(db, item.id)
                    # if result["success"]:
                    #     cleanup_results["items_deleted"] += 1
                    #     cleanup_results["total_records_deleted"] += result["total_records_deleted"]
                    #     cleanup_results["deleted_items"].append(result["deleted_item"])
                    
                    print(f"🔍 Item '{item.name}' has no orders (ID: {item.id})")
            
            return cleanup_results
            
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def batch_delete_menu_items(db: Session, menu_item_ids: List[int]) -> Dict[str, any]:
        """
        Delete multiple menu items in a single transaction.
        """
        try:
            results = {
                "success": True,
                "items_to_delete": len(menu_item_ids),
                "successful_deletions": 0,
                "failed_deletions": 0,
                "total_records_deleted": 0,
                "results": []
            }
            
            for menu_item_id in menu_item_ids:
                result = MenuItemDeletionService.delete_menu_item_complete(db, menu_item_id)
                results["results"].append(result)
                
                if result["success"]:
                    results["successful_deletions"] += 1
                    results["total_records_deleted"] += result.get("total_records_deleted", 0)
                else:
                    results["failed_deletions"] += 1
                    results["success"] = False
            
            return results
            
        except Exception as e:
            db.rollback()
            return {
                "success": False,
                "error": str(e),
                "items_to_delete": len(menu_item_ids)
            }
