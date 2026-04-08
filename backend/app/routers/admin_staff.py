from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.staff import StaffCreate, StaffResponse, StaffUpdate
from app.models.user import User
from app.core.security import hash_password
from app.core.dependencies import admin_only, super_admin_only, get_current_user

router = APIRouter(prefix="/api/admin/users", tags=["Admin Users"])


@router.get("/", response_model=List[StaffResponse])
def get_users(
    skip: int = 0,
    limit: int = 100,
    role: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_only)
):
    query = db.query(User)
    
    # Filter by role if provided
    if role:
        query = query.filter(User.role == role)
    else:
        # Show all users except Super Admins (for regular Admins)
        # Super Admins can see everyone
        if current_user.role != "SUPER_ADMIN":
             query = query.filter(User.role.in_(["ADMIN", "STAFF"]))
        # Super Admins can see all users including other Super Admins

    return query.offset(skip).limit(limit).all()


@router.post("/", response_model=StaffResponse)
def create_user(
    data: StaffCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(admin_only)
):
    # Only Super Admin can create other Admins
    if data.role == "ADMIN" and current_user.role != "SUPER_ADMIN":
        raise HTTPException(status_code=403, detail="Only Super Admin can create Admins")
        
    # Only Super Admin can create Super Admins (if we allow that)
    if data.role == "SUPER_ADMIN" and current_user.role != "SUPER_ADMIN":
        raise HTTPException(status_code=403, detail="Only Super Admin can create Super Admins")

    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        fullname=data.fullname,
        email=data.email,
        password_hash=hash_password(data.password),
        role=data.role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.put("/{user_id}", response_model=StaffResponse)
def update_user(
    user_id: int,
    data: StaffUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(super_admin_only)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Permission check: modifying admins/super_admins
    if user.role in ["ADMIN", "SUPER_ADMIN"] and current_user.role != "SUPER_ADMIN":
         # Admin cannot modify other Admins or Super Admin
         # Exception: Admin modifying themselves? No, this is management endpoint.
         raise HTTPException(status_code=403, detail="Insufficient permissions to modify this user")

    if data.role and data.role in ["ADMIN", "SUPER_ADMIN"] and current_user.role != "SUPER_ADMIN":
        raise HTTPException(status_code=403, detail="Only Super Admin can assign Admin roles")

    if data.fullname:
        user.fullname = data.fullname
    if data.email:
        user.email = data.email
    if data.role:
        user.role = data.role
    if data.is_active is not None:
        user.is_active = data.is_active

    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_only)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.role in ["ADMIN", "SUPER_ADMIN"] and current_user.role != "SUPER_ADMIN":
        raise HTTPException(status_code=403, detail="Insufficient permissions to delete this user")
    
    if user.id == current_user.id:
         raise HTTPException(status_code=400, detail="Cannot delete yourself")

    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}

