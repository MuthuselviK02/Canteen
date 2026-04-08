import sqlite3

conn = sqlite3('../canteen.db')
cursor = conn.cursor()

# Check total orders
cursor.execute('SELECT COUNT(*) FROM orders')
total_orders = cursor.fetchone()[0]
print(f'Total orders: {total_orders}')

# Check recent orders
cursor.execute('SELECT created_at, total_amount, status FROM orders ORDER BY created_at DESC LIMIT 5')
recent_orders = cursor.fetchall()
print('Recent orders:')
for row in recent_orders:
    print(f'  {row}')

# Check menu items for context
cursor.execute('SELECT COUNT(*) FROM menu_items')
total_menu_items = cursor.fetchone()[0]
print(f'Total menu items: {total_menu_items}')

conn.close()
