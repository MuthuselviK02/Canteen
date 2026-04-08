from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import hash_password, verify_password, create_access_token
from fastapi import HTTPException

ADMIN_DOMAIN = "@admin.com"
STAFF_DOMAIN = "@staff.com"


def authenticate_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({
        "user_id": user.id,
        "role": user.role
    })

    return token


def register_user(db: Session, fullname: str, email: str, password: str):
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=400, detail="Email already exists")

    user = User(
        fullname=fullname,
        email=email,
        password_hash=hash_password(password),
        role="USER"
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    return user
