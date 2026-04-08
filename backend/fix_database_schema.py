import sys
sys.path.append('.')
from app.database.session import engine, SessionLocal
from app.database.base import Base
from sqlalchemy import text

print('🔧 === DATABASE SCHEMA FIX ===')
print()

db = SessionLocal()

try:
    print('1. Checking if total_amount column exists in orders table...')
    
    # Check if the column exists
    result = db.execute(text("""
        SELECT COUNT(*) as count 
        FROM pragma_table_info('orders') 
        WHERE name = 'total_amount'
    """))
    
    column_exists = result.fetchone()[0] > 0
    
    if column_exists:
        print('✅ total_amount column already exists')
    else:
        print('❌ total_amount column missing - adding it...')
        
        # Add the missing column
        db.execute(text("""
            ALTER TABLE orders 
            ADD COLUMN total_amount REAL DEFAULT 0.0
        """))
        
        db.commit()
        print('✅ total_amount column added successfully')
    
    print()
    print('2. Checking orders table structure...')
    
    # Show table structure
    result = db.execute(text("PRAGMA table_info(orders)"))
    columns = result.fetchall()
    
    print('Orders table columns:')
    for column in columns:
        print(f'  - {column[1]} ({column[2]})')
    
    print()
    print('3. Testing basic order creation...')
    
    # Test creating a simple order
    test_order_data = {
        'user_id': 1,
        'status': 'Pending',
        'queue_position': 1,
        'predicted_wait_time': 15,
        'total_amount': 150.0
    }
    
    # Insert directly using raw SQL to bypass model issues
    db.execute(text("""
        INSERT INTO orders (user_id, status, queue_position, predicted_wait_time, total_amount, created_at)
        VALUES (:user_id, :status, :queue_position, :predicted_wait_time, :total_amount, datetime('now'))
    """), test_order_data)
    
    db.commit()
    
    # Get the inserted order
    result = db.execute(text("SELECT * FROM orders ORDER BY id DESC LIMIT 1"))
    order = result.fetchone()
    
    if order:
        print(f'✅ Test order created successfully: ID {order[0]}')
        print(f'   Total amount: ₹{order[5]}')
    else:
        print('❌ Failed to create test order')
    
    print()
    print('✅ Database schema fix completed!')
    
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()
    db.rollback()

finally:
    db.close()
