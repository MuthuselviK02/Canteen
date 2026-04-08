from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import hash_password

ADMIN_EMAIL = "superadmin@admin.com"
ADMIN_PASSWORD = "admin@1230"


def seed_admin(db: Session):
    admin = db.query(User).filter(User.email == ADMIN_EMAIL).first()
    if admin:
        return

    admin = User(
        fullname="Super Admin",
        email=ADMIN_EMAIL,
        password_hash=hash_password(ADMIN_PASSWORD),
        role="SUPER_ADMIN"
    )

    db.add(admin)
    db.commit()
