import sqlite3
import os

db_path = os.path.join(os.getcwd(), 'canteen.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print('=== ALL TABLES IN DATABASE ===')
cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
tables = cursor.fetchall()

for table_name, in tables:
    print(f'Table: {table_name}')

print('\n=== CHECKING FOR MENU ITEM REFERENCES ===')

# Check specific tables that likely reference menu items
tables_to_check = ['order_items', 'inventory', 'inventory_logs', 'inventory_stock_updates', 'demand_forecasts', 'preparation_time_predictions']

for table in tables_to_check:
    try:
        cursor.execute(f'SELECT COUNT(*) FROM {table}')
        count = cursor.fetchone()[0]
        print(f'{table}: {count} records')
        
        if count > 0:
            cursor.execute(f'SELECT * FROM {table} LIMIT 1')
            columns = [description[0] for description in cursor.description]
            print(f'  Columns: {columns}')
    except Exception as e:
        print(f'{table}: Error - {e}')

conn.close()
