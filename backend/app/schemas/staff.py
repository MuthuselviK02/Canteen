from pydantic import BaseModel, EmailStr

class StaffCreate(BaseModel):
    fullname: str
    email: EmailStr
    password: str
    role: str = "STAFF"  # Default to STAFF, but can be set to ADMIN

class StaffUpdate(BaseModel):
    fullname: str | None = None
    email: EmailStr | None = None
    role: str | None = None
    is_active: bool | None = None

class StaffResponse(BaseModel):
    id: int
    fullname: str
    email: EmailStr
    role: str
    is_active: bool

    class Config:
        from_attributes = True
