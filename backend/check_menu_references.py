import sqlite3
import os

# Get database schema to understand relationships
db_path = os.path.join(os.getcwd(), 'canteen.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print('=== DATABASE TABLES THAT REFERENCE MENU_ITEMS ===')

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

# Check each table for foreign key references to menu_items
for table_name, in tables:
    try:
        cursor.execute(f'PRAGMA table_info({table_name[0]})')
        columns = cursor.fetchall()
        
        for col in columns:
            col_name = col[1]
            if 'menu_item' in col_name.lower() or 'item_id' in col_name.lower():
                print(f'📋 Table: {table_name[0]} - Column: {col_name}')
                
                # Show sample data count
                try:
                    cursor.execute(f'SELECT COUNT(*) FROM {table_name[0]} WHERE {col_name} IS NOT NULL')
                    count = cursor.fetchone()[0]
                    print(f'   Records with menu item references: {count}')
                except:
                    print(f'   Could not count records')
                print()
    except Exception as e:
        pass

conn.close()
