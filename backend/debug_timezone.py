import sys
sys.path.append('.')
from app.database.session import SessionLocal
from app.models.order import Order
from datetime import datetime
import pytz

print('🕐 === TIMEZONE DEBUG ===')
print()

# Get current times
utc_now = datetime.utcnow()
ist_now = datetime.now(pytz.timezone('Asia/Kolkata'))

print(f'UTC Now: {utc_now}')
print(f'IST Now: {ist_now}')
print(f'IST Now (naive): {datetime.now()}')
print()

# Check database orders
db = SessionLocal()
orders = db.query(Order).limit(5).all()

print('📊 Recent Orders from Database:')
for order in orders:
    print(f'Order #{order.id}:')
    print(f'  Created At (DB): {order.created_at}')
    print(f'  Started At (DB): {order.started_preparation_at}')
    print(f'  Ready At (DB): {order.ready_at}')
    print(f'  Completed At (DB): {order.completed_at}')
    print()

db.close()

# Test IST conversion
test_time = utc_now
print('🧪 IST Conversion Test:')
print(f'Original UTC: {test_time}')

# Manual IST conversion (like frontend)
utc_time = test_time.timestamp() * 1000
ist_offset = 5.5 * 60 * 60 * 1000
ist_time = utc_time + ist_offset
converted = datetime.fromtimestamp(ist_time / 1000)
print(f'Manual IST: {converted}')

# Using pytz
ist_tz = pytz.timezone('Asia/Kolkata')
utc_with_tz = pytz.UTC.localize(test_time)
ist_with_tz = utc_with_tz.astimezone(ist_tz)
print(f'PyTZ IST: {ist_with_tz}')
