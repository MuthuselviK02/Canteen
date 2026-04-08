"""
Database indexes for performance optimization.
Run this once to create indexes for faster queries.
"""
from sqlalchemy import text
from app.database.session import engine

def create_indexes():
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_demand_forecasts_date_period ON demand_forecasts(forecast_date, forecast_period);",
        "CREATE INDEX IF NOT EXISTS idx_demand_forecasts_menu_item ON demand_forecasts(menu_item_id);",
        "CREATE INDEX IF NOT EXISTS idx_menu_items_category ON menu_items(category);",
        "CREATE INDEX IF NOT EXISTS idx_orders_status_created ON orders(status, created_at);",
        "CREATE INDEX IF NOT EXISTS idx_order_items_menu_item ON order_items(menu_item_id);",
        "CREATE INDEX IF NOT EXISTS idx_inventory_menu_item ON inventory(menu_item_id);",
    ]

    with engine.connect() as conn:
        for idx_sql in indexes:
            print(f"Executing: {idx_sql}")
            conn.execute(text(idx_sql))
        conn.commit()
    print("All indexes created/verified.")

if __name__ == "__main__":
    create_indexes()
