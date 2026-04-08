from app.database.session import get_db
from app.services.historical_analytics_service import HistoricalAnalyticsService
from datetime import datetime, timedelta
from sqlalchemy import and_
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.menu import MenuItem
import sys

# Check item performance data
db = next(get_db())
try:
    print('🔍 INVESTIGATING LOW SELLING ITEMS ISSUE')
    print('=' * 50)
    
    # Get raw item performance data
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=30)
    
    # Get order items with menu and order details
    order_items_query = db.query(OrderItem, MenuItem, Order).join(
        MenuItem, OrderItem.menu_item_id == MenuItem.id
    ).join(
        Order, OrderItem.order_id == Order.id
    ).filter(
        and_(
            Order.created_at >= start_date,
            Order.created_at < end_date,
            Order.status.in_(['completed', 'paid'])
        )
    ).all()
    
    # Aggregate item performance
    item_stats = {}
    for order_item, menu_item, order in order_items_query:
        item_id = menu_item.id
        if item_id not in item_stats:
            item_stats[item_id] = {
                "name": menu_item.name,
                "category": menu_item.category,
                "price": menu_item.price or 0,
                "total_quantity": 0,
                "total_orders": set(),
                "total_revenue": 0
            }
        
        item_stats[item_id]["total_quantity"] += order_item.quantity
        item_stats[item_id]["total_orders"].add(order_item.order_id)
        item_stats[item_id]["total_revenue"] += (menu_item.price or 0) * order_item.quantity
    
    # Convert sets to counts
    for item_id, stats in item_stats.items():
        stats["total_orders"] = len(stats["total_orders"])
        stats["avg_quantity_per_order"] = stats["total_quantity"] / stats["total_orders"] if stats["total_orders"] > 0 else 0
    
    print(f'Total items found: {len(item_stats)}')
    print('\n📊 ITEM ORDER BREAKDOWN:')
    
    items_by_orders = sorted(item_stats.values(), key=lambda x: x["total_orders"], reverse=True)
    
    for i, item in enumerate(items_by_orders):
        print(f'{i+1:2d}. {item["name"]:20s} - Orders: {item["total_orders"]:2d}, Revenue: ₹{item["total_revenue"]:6.2f}')
    
    # Check low selling filter
    print('\n🔍 LOW SELLING FILTER ANALYSIS:')
    low_selling_candidates = [stats for stats in item_stats.values() if stats["total_orders"] >= 5]
    print(f'Items with >= 5 orders: {len(low_selling_candidates)}')
    
    if len(low_selling_candidates) == 0:
        print('❌ NO ITEMS meet the >= 5 orders requirement!')
        print('This is why low selling items section is empty.')
        
        print('\n💡 SUGGESTED FIXES:')
        print('1. Lower the minimum order requirement from 5 to 1')
        print('2. Or use a percentage-based approach')
        print('3. Or show items with lowest revenue regardless of order count')
    
    # Show what would happen with lower threshold
    low_selling_candidates_1 = [stats for stats in item_stats.values() if stats["total_orders"] >= 1]
    if len(low_selling_candidates_1) > 0:
        low_selling_1 = sorted(low_selling_candidates_1, key=lambda x: x["total_revenue"])[:5]
        print(f'\n📋 LOW SELLING ITEMS (with >= 1 order):')
        for i, item in enumerate(low_selling_1):
            print(f'{i+1}. {item["name"]} - Orders: {item["total_orders"]}, Revenue: ₹{item["total_revenue"]:.2f}')
    
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()
finally:
    db.close()
