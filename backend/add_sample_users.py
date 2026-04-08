import sys
sys.path.append('.')
from app.database.session import SessionLocal
from app.models.user import User
from werkzeug.security import generate_password_hash

print('=== Adding Sample Users for Testing ===')

db = SessionLocal()

sample_users = [
    {
        'email': 'testuser1@example.com',
        'password': 'password123',
        'name': 'Test User 1',
        'role': 'user'
    },
    {
        'email': 'testuser2@example.com',
        'password': 'password123',
        'name': 'Test User 2',
        'role': 'user'
    },
    {
        'email': 'kitchen@example.com',
        'password': 'kitchen123',
        'name': 'Kitchen Staff',
        'role': 'kitchen'
    },
    {
        'email': 'admin@example.com',
        'password': 'admin123',
        'name': 'Admin User',
        'role': 'admin'
    }
]

try:
    added_count = 0
    for user_data in sample_users:
        # Check if user already exists
        existing = db.query(User).filter(User.email == user_data['email']).first()
        if existing:
            print(f"⚠️  User '{user_data['email']}' already exists, skipping...")
            continue
        
        user = User(
            email=user_data['email'],
            password_hash=generate_password_hash(user_data['password']),
            fullname=user_data['name'],
            role=user_data['role'],
            is_active=True
        )
        
        db.add(user)
        added_count += 1
        print(f"✅ Added: {user_data['email']} ({user_data['role']})")
    
    db.commit()
    
    print(f"\n🎉 Successfully added {added_count} sample users!")
    print("\n👥 User Accounts Created:")
    print("   superadmin@admin.com (admin123) - Super Admin")
    print("   admin@example.com (admin123) - Admin")
    print("   kitchen@example.com (kitchen123) - Kitchen Staff")
    print("   testuser1@example.com (password123) - Regular User")
    print("   testuser2@example.com (password123) - Regular User")
    
except Exception as e:
    print(f"❌ Error adding users: {e}")
    db.rollback()
finally:
    db.close()
