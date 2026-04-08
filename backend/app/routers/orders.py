from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import time

from app.database.session import get_db
from app.schemas.order import OrderCreate, OrderResponse
from app.core.dependencies import get_current_user
from app.orchestrator.order_orchestrator import place_order
from app.services.order_service import (
    get_user_orders_with_items, 
    get_order_with_items,
    update_order_status,
    get_order_time_summary,
    update_orders_queue,
    delete_order
)

router = APIRouter(prefix="/api/orders", tags=["Orders"])

# Simple rate limiting for status updates
last_update_times = {}
RATE_LIMIT_SECONDS = 2  # Allow max 1 update per 2 seconds per order

def check_rate_limit(order_id: int):
    """Simple rate limiting to prevent rapid consecutive updates"""
    current_time = time.time()
    last_time = last_update_times.get(order_id, 0)
    
    if current_time - last_time < RATE_LIMIT_SECONDS:
        raise HTTPException(
            status_code=429, 
            detail=f"Rate limit exceeded. Please wait {RATE_LIMIT_SECONDS - (current_time - last_time):.1f} seconds before updating this order again."
        )
    
    last_update_times[order_id] = current_time


@router.post("/", response_model=OrderResponse)
def create_order(
    data: OrderCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """
    USER places an order with current timestamp.
    """
    order = place_order(
        db,
        user.id,
        data.items,
        data.available_time
    )
    
    # Return order with menu item details and dynamic time
    return get_order_with_items(db, order.id, user.id)


@router.get("/", response_model=List[OrderResponse])
def get_user_orders(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """
    USER fetches all their orders with dynamic wait times.
    """
    return get_user_orders_with_items(db, user.id)


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """
    USER fetches their own order with dynamic time calculations.
    """
    return get_order_with_items(db, order_id, user.id)


@router.put("/{order_id}/status")
def update_order_status_endpoint(
    order_id: int,
    status: str,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """
    Update order status with timestamp tracking and concurrent update protection.
    This endpoint handles staff updates to order status safely with rate limiting.
    """
    try:
        # Apply rate limiting
        check_rate_limit(order_id)
        
        print(f"Updating order {order_id} to status '{status}'")
        order = update_order_status(db, order_id, status)
        
        if order:
            print(f"Order {order_id} update successful - Status: {order.status}, Started: {order.started_preparation_at}, Ready: {order.ready_at}, Completed: {order.completed_at}")
            
            return {
                "message": f"Order {order_id} status updated to {status}", 
                "order_id": order_id,
                "new_status": order.status,
                "predicted_wait_time": order.predicted_wait_time,
                "queue_position": order.queue_position,
                "updated_at": time.time(),
                "debug": {
                    "started_preparation_at": order.started_preparation_at.isoformat() if order.started_preparation_at else None,
                    "ready_at": order.ready_at.isoformat() if order.ready_at else None,
                    "completed_at": order.completed_at.isoformat() if order.completed_at else None
                }
            }
        else:
            raise HTTPException(status_code=404, detail="Order not found")
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error updating order {order_id} status: {e}")
        raise HTTPException(status_code=500, detail="Failed to update order status. Please try again.")


@router.get("/{order_id}/time-summary")
def get_order_time_summary_endpoint(
    order_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """
    Get comprehensive time summary for an order.
    """
    summary = get_order_time_summary(db, order_id)
    if summary:
        return summary
    else:
        return {"error": "Order not found"}, 404


@router.post("/update-queue")
def update_queue_endpoint(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """
    Update queue positions and recalculate wait times for all pending orders.
    This should be called periodically in production.
    """
    try:
        updated_count = update_orders_queue(db)
        return {"message": f"Updated {updated_count} orders in queue", "updated_count": updated_count}
    except Exception as e:
        print(f"Error updating queue: {e}")
        raise HTTPException(status_code=500, detail="Failed to update queue")


@router.post("/bulk-status-update")
def bulk_status_update_endpoint(
    updates: List[Dict[str, Any]],
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """
    Bulk update multiple order statuses at once.
    This is optimized for staff dashboard operations.
    """
    try:
        results = []
        errors = []
        
        # Process updates in order to maintain consistency
        for update in sorted(updates, key=lambda x: x.get('order_id', 0)):
            order_id = update.get('order_id')
            new_status = update.get('status')
            
            if not order_id or not new_status:
                errors.append(f"Invalid update data: {update}")
                continue
            
            try:
                # Apply rate limiting for bulk updates (more lenient)
                check_rate_limit(order_id)
                
                order = update_order_status(db, order_id, new_status)
                if order:
                    results.append({
                        "order_id": order_id,
                        "old_status": order.status,
                        "new_status": new_status,
                        "predicted_wait_time": order.predicted_wait_time,
                        "queue_position": order.queue_position,
                        "success": True
                    })
                else:
                    errors.append(f"Order {order_id} not found")
                    
            except Exception as e:
                errors.append(f"Order {order_id}: {str(e)}")
        
        return {
            "message": f"Processed {len(updates)} updates",
            "successful_updates": len(results),
            "errors": len(errors),
            "results": results,
            "errors": errors
        }
        
    except Exception as e:
        print(f"Error in bulk status update: {e}")
        raise HTTPException(status_code=500, detail="Failed to process bulk updates")


@router.post("/force-queue-refresh")
def force_queue_refresh_endpoint(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """
    Force refresh all queue positions and recalculate all wait times.
    Use this when queue positions appear incorrect.
    """
    try:
        # Get all orders and recalculate everything
        from app.models.order import Order
        
        all_orders = db.query(Order).all()
        updated_count = 0
        
        for order in all_orders:
            old_wait_time = order.predicted_wait_time
            new_wait_time = update_orders_queue(db)
            
            if old_wait_time != new_wait_time:
                updated_count += 1
        
        return {
            "message": f"Force refreshed queue positions",
            "total_orders": len(all_orders),
            "updated_orders": updated_count
        }
        
    except Exception as e:
        print(f"Error in force queue refresh: {e}")
        raise HTTPException(status_code=500, detail="Failed to refresh queue")


@router.get("/live-queue-status")
def get_live_queue_status(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """
    Get real-time queue status with dynamic wait times.
    This endpoint provides production-ready live updates.
    """
    try:
        from app.models.order import Order
        from app.services.order_time_service import OrderTimeService
        
        # Get all pending and preparing orders with real-time calculations
        active_orders = db.query(Order).filter(
            Order.status.in_(["pending", "preparing"])
        ).order_by(Order.queue_position).all()
        
        queue_status = []
        current_time = time.time()
        
        for order in active_orders:
            # Calculate real-time wait time
            dynamic_wait_time = OrderTimeService.calculate_dynamic_wait_time(order, db)
            
            # Update the order's predicted wait time in real-time
            if order.predicted_wait_time != dynamic_wait_time:
                order.predicted_wait_time = dynamic_wait_time
                # Don't commit here to avoid database spam, just calculate
            
            queue_item = {
                "order_id": order.id,
                "queue_position": order.queue_position,
                "status": order.status,
                "predicted_wait_time": dynamic_wait_time,
                "created_at": order.created_at.isoformat() if order.created_at else None,
                "started_preparation_at": order.started_preparation_at.isoformat() if order.started_preparation_at else None,
                "current_time": current_time,
                "time_remaining": dynamic_wait_time if order.status == "pending" else max(0, dynamic_wait_time),
                "is_user_order": order.user_id == user.id
            }
            
            # Add user info for staff
            if user.role in ['ADMIN', 'SUPER_ADMIN', 'STAFF']:
                queue_item["user_id"] = order.user_id
            
            queue_status.append(queue_item)
        
        # Calculate kitchen workload
        kitchen_stats = {
            "total_pending": len([o for o in active_orders if o.status == "pending"]),
            "total_preparing": len([o for o in active_orders if o.status == "preparing"]),
            "estimated_kitchen_clear_time": max([o.predicted_wait_time for o in active_orders], default=0),
            "average_wait_time": sum([o.predicted_wait_time for o in active_orders]) / len(active_orders) if active_orders else 0,
            "last_updated": current_time
        }
        
        return {
            "queue_status": queue_status,
            "kitchen_stats": kitchen_stats,
            "timestamp": current_time,
            "update_frequency": "real-time"
        }
        
    except Exception as e:
        print(f"Error getting live queue status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get live queue status")


@router.get("/my-live-orders")
def get_my_live_orders(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """
    Get user's orders with real-time wait time updates.
    This provides production-ready live timing for customers.
    """
    try:
        from app.services.order_time_service import OrderTimeService
        
        # Get user's orders
        user_orders = get_user_orders_with_items(db, user.id)
        
        live_orders = []
        current_time = time.time()
        
        for order in user_orders:
            # Calculate real-time wait time
            dynamic_wait_time = OrderTimeService.calculate_dynamic_wait_time(order, db)
            
            live_order = {
                "id": order.id,
                "status": order.status,
                "queue_position": order.queue_position,
                "predicted_wait_time": dynamic_wait_time,
                "created_at": order.created_at.isoformat() if order.created_at else None,
                "started_preparation_at": order.started_preparation_at.isoformat() if order.started_preparation_at else None,
                "ready_at": order.ready_at.isoformat() if order.ready_at else None,
                "completed_at": order.completed_at.isoformat() if order.completed_at else None,
                "time_remaining": max(0, dynamic_wait_time) if order.status in ["pending", "preparing"] else 0,
                "progress_percentage": OrderTimeService._calculate_progress_percentage(order, dynamic_wait_time, db),
                "estimated_completion": current_time + (dynamic_wait_time * 60) if order.status in ["pending", "preparing"] else None,
                "items": [
                    {
                        "name": item.menu_item.name if item.menu_item else "Unknown",
                        "quantity": item.quantity,
                        "prep_time": item.menu_item.base_prep_time if item.menu_item and item.menu_item.base_prep_time else 10
                    }
                    for item in getattr(order, 'order_items', [])
                ]
            }
            
            live_orders.append(live_order)
        
        return {
            "orders": live_orders,
            "timestamp": current_time,
            "update_frequency": "real-time"
        }
        
    except Exception as e:
        print(f"Error getting user's live orders: {e}")
        raise HTTPException(status_code=500, detail="Failed to get live orders")


@router.post("/auto-refresh-queue")
def auto_refresh_queue(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """
    Automatic queue refresh endpoint.
    This should be called every 30-60 seconds in production for real-time updates.
    """
    try:
        # Update all queue positions and recalculate wait times
        updated_count = update_orders_queue(db)
        
        # Get current queue stats
        from app.models.order import Order
        pending_orders = db.query(Order).filter(Order.status == "pending").count()
        preparing_orders = db.query(Order).filter(Order.status == "preparing").count()
        
        return {
            "message": "Queue auto-refreshed",
            "updated_orders": updated_count,
            "queue_stats": {
                "pending": pending_orders,
                "preparing": preparing_orders,
                "total_active": pending_orders + preparing_orders
            },
            "timestamp": time.time(),
            "next_refresh_in": 30  # seconds
        }
        
    except Exception as e:
        print(f"Error in auto refresh: {e}")
        raise HTTPException(status_code=500, detail="Failed to auto-refresh queue")


@router.get("/{order_id}/live-status")
def get_order_live_status(
    order_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """
    Get real-time status for a specific order.
    Provides production-ready live tracking.
    """
    try:
        from app.services.order_time_service import OrderTimeService
        
        # Get order with security check
        order = get_order_with_items(db, order_id, user.id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Calculate real-time wait time
        dynamic_wait_time = OrderTimeService.calculate_dynamic_wait_time(order, db)
        
        # Get comprehensive time summary
        time_summary = OrderTimeService.get_order_time_summary(order)
        
        live_status = {
            "order_id": order.id,
            "status": order.status,
            "queue_position": order.queue_position,
            "predicted_wait_time": dynamic_wait_time,
            "time_remaining": max(0, dynamic_wait_time) if order.status in ["pending", "preparing"] else 0,
            "progress_percentage": OrderTimeService._calculate_progress_percentage(order, dynamic_wait_time, db),
            "estimated_completion": time.time() + (dynamic_wait_time * 60) if order.status in ["pending", "preparing"] else None,
            "time_summary": time_summary,
            "items": [
                {
                    "name": item.menu_item.name if item.menu_item else "Unknown",
                    "quantity": item.quantity,
                    "prep_time": item.menu_item.base_prep_time if item.menu_item and item.menu_item.base_prep_time else 10
                }
                for item in getattr(order, 'order_items', [])
            ],
            "timestamps": {
                "created_at": order.created_at.isoformat() if order.created_at else None,
                "started_preparation_at": order.started_preparation_at.isoformat() if order.started_preparation_at else None,
                "ready_at": order.ready_at.isoformat() if order.ready_at else None,
                "completed_at": order.completed_at.isoformat() if order.completed_at else None
            },
            "live_tracking": {
                "is_active": order.status in ["pending", "preparing"],
                "last_updated": time.time(),
                "update_frequency": "real-time"
            }
        }
        
        return live_status
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting order live status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get live order status")


@router.get("/production/queue-status")
def get_production_queue_status(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """
    Production-ready queue status with real-time updates.
    This endpoint provides comprehensive queue analytics for staff.
    """
    try:
        from app.services.production_queue_manager import production_queue_manager
        
        # Get real-time queue status
        status = production_queue_manager.get_real_time_queue_status()
        
        # Add user-specific info
        if user.role in ['ADMIN', 'SUPER_ADMIN', 'STAFF']:
            status["user_role"] = user.role
            status["can_manage_queue"] = True
        else:
            status["user_role"] = user.role
            status["can_manage_queue"] = False
        
        return status
        
    except Exception as e:
        print(f"Error getting production queue status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get production queue status")


@router.post("/production/start-auto-updates")
def start_production_auto_updates(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """
    Start automatic queue updates for production.
    Only staff can start this feature.
    """
    try:
        if user.role not in ['ADMIN', 'SUPER_ADMIN', 'STAFF']:
            raise HTTPException(status_code=403, detail="Only staff can start production updates")
        
        from app.services.production_queue_manager import production_queue_manager
        
        production_queue_manager.start_background_updates()
        
        return {
            "message": "Production auto-updates started",
            "update_interval": production_queue_manager.update_interval,
            "started_by": user.email,
            "timestamp": time.time()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error starting production updates: {e}")
        raise HTTPException(status_code=500, detail="Failed to start production updates")


@router.post("/production/stop-auto-updates")
def stop_production_auto_updates(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """
    Stop automatic queue updates for production.
    Only staff can stop this feature.
    """
    try:
        if user.role not in ['ADMIN', 'SUPER_ADMIN', 'STAFF']:
            raise HTTPException(status_code=403, detail="Only staff can stop production updates")
        
        from app.services.production_queue_manager import production_queue_manager
        
        production_queue_manager.stop_background_updates()
        
        return {
            "message": "Production auto-updates stopped",
            "stopped_by": user.email,
            "timestamp": time.time(),
            "final_stats": production_queue_manager.stats
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error stopping production updates: {e}")
        raise HTTPException(status_code=500, detail="Failed to stop production updates")


@router.post("/production/force-update")
def force_production_update(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """
    Force immediate queue update.
    Only staff can force updates.
    """
    try:
        if user.role not in ['ADMIN', 'SUPER_ADMIN', 'STAFF']:
            raise HTTPException(status_code=403, detail="Only staff can force updates")
        
        from app.services.production_queue_manager import production_queue_manager
        
        result = production_queue_manager.force_immediate_update()
        
        return {
            "message": "Production update forced",
            "forced_by": user.email,
            "result": result,
            "timestamp": time.time()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error forcing production update: {e}")
        raise HTTPException(status_code=500, detail="Failed to force production update")


@router.get("/production/kitchen-analytics")
def get_kitchen_analytics(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """
    Get comprehensive kitchen analytics for production optimization.
    Only staff can access this endpoint.
    """
    try:
        if user.role not in ['ADMIN', 'SUPER_ADMIN', 'STAFF']:
            raise HTTPException(status_code=403, detail="Only staff can access kitchen analytics")
        
        from app.models.order import Order
        from app.services.order_time_service import OrderTimeService
        from datetime import datetime, timedelta
        
        # Get today's orders
        today = datetime.utcnow().date()
        today_orders = db.query(Order).filter(
            Order.created_at >= today
        ).all()
        
        # Calculate analytics
        analytics = {
            "today_stats": {
                "total_orders": len(today_orders),
                "completed_orders": len([o for o in today_orders if o.status == "completed"]),
                "pending_orders": len([o for o in today_orders if o.status == "pending"]),
                "preparing_orders": len([o for o in today_orders if o.status == "preparing"]),
                "average_preparation_time": 0,
                "peak_hour": None
            },
            "current_workload": {
                "active_orders": len([o for o in today_orders if o.status in ["pending", "preparing"]]),
                "estimated_clear_time": 0,
                "kitchen_efficiency": 0
            },
            "item_performance": {},
            "time_based_analytics": {
                "orders_by_hour": {},
                "average_wait_times": []
            }
        }
        
        # Calculate preparation times
        completed_orders = [o for o in today_orders if o.status == "completed" and o.completed_at and o.started_preparation_at]
        if completed_orders:
            prep_times = [(o.completed_at - o.started_preparation_at).total_seconds() / 60 for o in completed_orders]
            analytics["today_stats"]["average_preparation_time"] = sum(prep_times) / len(prep_times)
        
        # Calculate current workload
        active_orders = [o for o in today_orders if o.status in ["pending", "preparing"]]
        if active_orders:
            wait_times = [OrderTimeService.calculate_dynamic_wait_time(o, db) for o in active_orders]
            analytics["current_workload"]["estimated_clear_time"] = max(wait_times) if wait_times else 0
            
            # Calculate efficiency
            preparing_count = len([o for o in active_orders if o.status == "preparing"])
            pending_count = len([o for o in active_orders if o.status == "pending"])
            if pending_count > 0:
                analytics["current_workload"]["kitchen_efficiency"] = min(100.0, (preparing_count / pending_count) * 100)
        
        return {
            "analytics": analytics,
            "generated_by": user.email,
            "timestamp": time.time()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting kitchen analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get kitchen analytics")


@router.delete("/{order_id}")
def delete_order_endpoint(
    order_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """
    Delete an order. Only completed orders can be deleted by users.
    Staff can delete any order.
    """
    try:
        # Check if order exists and belongs to user (or user is staff)
        from app.models.order import Order
        
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Users can only delete their own completed orders
        # Staff can delete any order
        if user.role not in ['ADMIN', 'SUPER_ADMIN', 'STAFF']:
            if order.user_id != user.id:
                raise HTTPException(status_code=403, detail="You can only delete your own orders")
            if order.status != 'completed':
                raise HTTPException(status_code=400, detail="Only completed orders can be deleted")
        
        # Delete the order (this will cascade delete order items)
        success = delete_order(db, order_id)
        
        if success:
            return {
                "message": f"Order {order_id} deleted successfully",
                "order_id": order_id,
                "deleted_by": user.email,
                "deleted_at": time.time()
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to delete order")
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error deleting order {order_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete order")
