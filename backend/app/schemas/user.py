from pydantic import BaseModel, EmailStr

class UserResponse(BaseModel):
    id: int
    fullname: str
    email: EmailStr
    role: str

    class Config:
        from_attributes = True
