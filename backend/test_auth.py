from app.database.session import get_db
from app.models.user import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

db = next(get_db())
try:
    user = db.query(User).filter(User.email == 'superadmin@admin.com').first()
    if user:
        # Test password verification
        test_password = 'admin123'
        is_valid = pwd_context.verify(test_password, user.password_hash)
        print(f'Password verification for "admin123": {is_valid}')
        
        # Test with common passwords
        for pwd in ['admin', 'password', '123456', 'superadmin']:
            is_valid = pwd_context.verify(pwd, user.password_hash)
            print(f'Password verification for "{pwd}": {is_valid}')
    else:
        print('User not found')
        
finally:
    db.close()
