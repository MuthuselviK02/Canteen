import sys
sys.path.append('.')
from app.database.session import SessionLocal
from app.models.user import User

print('=== Checking User Credentials ===')

db = SessionLocal()

try:
    users = db.query(User).all()
    print(f"📊 Total users: {len(users)}")
    
    print("\n👥 User List:")
    for user in users:
        print(f"   Email: {user.email}")
        print(f"   Name: {user.fullname}")
        print(f"   Role: {user.role}")
        print(f"   Active: {user.is_active}")
        print("---")
    
    # Test with superadmin
    superadmin = db.query(User).filter(User.email == "superadmin@admin.com").first()
    if superadmin:
        print(f"\n🔑 Superadmin found:")
        print(f"   Email: {superadmin.email}")
        print(f"   Role: {superadmin.role}")
        print(f"   Password hash: {superadmin.password_hash[:20]}...")
        
        # Test password verification
        from app.core.security import verify_password
        if verify_password("admin123", superadmin.password_hash):
            print("   ✅ Password 'admin123' verified")
        else:
            print("   ❌ Password verification failed")
    else:
        print("❌ Superadmin not found!")

except Exception as e:
    print(f"❌ Error: {e}")
finally:
    db.close()
