import sys
sys.path.append('.')
from app.database.session import SessionLocal
from app.models.menu import MenuItem

db = SessionLocal()
menu_items = db.query(MenuItem).all()
print(f'Found {len(menu_items)} menu items')
for item in menu_items[:3]:
    print(f'- {item.name} (ID: {item.id})')
db.close()
