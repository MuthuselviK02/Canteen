import threading
import time
import asyncio
from typing import Dict, Any
from sqlalchemy.orm import Session
from app.database.session import SessionLocal
from app.services.order_service import update_orders_queue
from app.services.order_time_service import OrderTimeService


class ProductionQueueManager:
    """
    Production-ready queue manager for real-time wait time updates.
    Handles automatic queue updates and kitchen workload optimization.
    """
    
    def __init__(self):
        self.is_running = False
        self.update_interval = 30  # seconds
        self.last_update_time = 0
        self.update_thread = None
        self.stats = {
            "total_updates": 0,
            "last_update_duration": 0,
            "average_orders_updated": 0,
            "errors": 0
        }
    
    def start_background_updates(self):
        """Start background thread for automatic queue updates."""
        if not self.is_running:
            self.is_running = True
            self.update_thread = threading.Thread(target=self._background_updater, daemon=True)
            self.update_thread.start()
            print("Production queue manager started")
    
    def stop_background_updates(self):
        """Stop background updates."""
        self.is_running = False
        if self.update_thread:
            self.update_thread.join(timeout=5)
        print("Production queue manager stopped")
    
    def _background_updater(self):
        """Background thread that updates queue positions and wait times."""
        while self.is_running:
            try:
                start_time = time.time()
                
                # Create database session for this thread
                db = SessionLocal()
                
                try:
                    # Update all queue positions and recalculate wait times
                    updated_count = update_orders_queue(db)
                    
                    # Update stats
                    self.stats["total_updates"] += 1
                    self.stats["last_update_duration"] = time.time() - start_time
                    self.stats["average_orders_updated"] = (
                        (self.stats["average_orders_updated"] * (self.stats["total_updates"] - 1) + updated_count) 
                        / self.stats["total_updates"]
                    )
                    
                    self.last_update_time = time.time()
                    
                    if updated_count > 0:
                        print(f"Queue auto-updated: {updated_count} orders refreshed in {self.stats['last_update_duration']:.2f}s")
                    
                except Exception as e:
                    self.stats["errors"] += 1
                    print(f"Error in background queue update: {e}")
                finally:
                    db.close()
                
                # Wait for next update
                time.sleep(self.update_interval)
                
            except Exception as e:
                print(f"Critical error in background updater: {e}")
                self.stats["errors"] += 1
                time.sleep(5)  # Brief pause before retry
    
    def get_real_time_queue_status(self) -> Dict[str, Any]:
        """Get current queue status with real-time calculations."""
        try:
            db = SessionLocal()
            
            from app.models.order import Order
            
            # Get all active orders
            active_orders = db.query(Order).filter(
                Order.status.in_(["pending", "preparing"])
            ).order_by(Order.queue_position).all()
            
            # Calculate real-time wait times
            queue_status = []
            total_wait_time = 0
            
            for order in active_orders:
                dynamic_wait_time = OrderTimeService.calculate_dynamic_wait_time(order, db)
                total_wait_time += dynamic_wait_time
                
                queue_status.append({
                    "order_id": order.id,
                    "queue_position": order.queue_position,
                    "status": order.status,
                    "predicted_wait_time": dynamic_wait_time,
                    "created_at": order.created_at.isoformat() if order.created_at else None,
                    "progress_percentage": OrderTimeService._calculate_progress_percentage(order, dynamic_wait_time, db)
                })
            
            kitchen_performance = {
                "total_active_orders": len(active_orders),
                "pending_orders": len([o for o in active_orders if o.status == "pending"]),
                "preparing_orders": len([o for o in active_orders if o.status == "preparing"]),
                "estimated_clear_time": max([o.predicted_wait_time for o in active_orders], default=0),
                "average_wait_time": total_wait_time / len(active_orders) if active_orders else 0,
                "kitchen_efficiency": self._calculate_kitchen_efficiency(active_orders)
            }
            
            db.close()
            
            return {
                "queue_status": queue_status,
                "kitchen_performance": kitchen_performance,
                "manager_stats": self.stats,
                "last_update": self.last_update_time,
                "update_frequency": self.update_interval,
                "is_running": self.is_running
            }
            
        except Exception as e:
            print(f"Error getting real-time queue status: {e}")
            return {"error": str(e)}
    
    def _calculate_kitchen_efficiency(self, active_orders) -> float:
        """Calculate kitchen efficiency based on order throughput."""
        try:
            if not active_orders:
                return 100.0
            
            # Efficiency based on how quickly orders are moving through the system
            preparing_count = len([o for o in active_orders if o.status == "preparing"])
            pending_count = len([o for o in active_orders if o.status == "pending"])
            
            # Ideal ratio: more preparing than pending
            if pending_count == 0:
                return 100.0
            
            efficiency = min(100.0, (preparing_count / pending_count) * 100)
            return efficiency
            
        except Exception:
            return 0.0
    
    def force_immediate_update(self) -> Dict[str, Any]:
        """Force immediate queue update and return results."""
        try:
            start_time = time.time()
            db = SessionLocal()
            
            updated_count = update_orders_queue(db)
            duration = time.time() - start_time
            
            db.close()
            
            return {
                "message": "Immediate queue update completed",
                "updated_orders": updated_count,
                "duration": duration,
                "timestamp": time.time()
            }
            
        except Exception as e:
            return {"error": str(e)}


# Global instance for production use
production_queue_manager = ProductionQueueManager()
