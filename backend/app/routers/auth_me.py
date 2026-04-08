from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/auth", tags=["Auth"])

@router.get("/me")
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Return the current authenticated user's info."""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "fullname": current_user.fullname,
        "role": current_user.role,
    }
