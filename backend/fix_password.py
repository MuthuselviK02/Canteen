from app.database.session import get_db
from app.models.user import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

db = next(get_db())
try:
    # Create a test password hash for 'admin123'
    test_hash = pwd_context.hash('admin123')
    print(f'Hash for "admin123": {test_hash}')
    
    # Check existing user
    user = db.query(User).filter(User.email == 'superadmin@admin.com').first()
    if user:
        print(f'Existing hash: {user.password_hash}')
        
        # Update password to admin123 for testing
        user.password_hash = test_hash
        db.commit()
        print('Updated password to "admin123" for testing')
    else:
        print('User not found')
        
finally:
    db.close()
