from datetime import datetime, timedelta
from jose import jwt
import hashlib
import base64
from app.core.config import settings

# Simple password hashing as temporary fix for bcrypt compatibility issue
def hash_password(password: str) -> str:
    # Use SHA-256 as temporary solution
    return base64.b64encode(hashlib.sha256(password.encode()).digest()).decode()

def verify_password(password: str, hashed: str) -> bool:
    # Use SHA-256 as temporary solution
    return hash_password(password) == hashed

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})
    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
