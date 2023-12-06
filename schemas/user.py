from pydantic import BaseModel, EmailStr, constr
from datetime import datetime
from typing import Optional
from Enum import StatusEnum


class UserBaseSchema(BaseModel):
    name: constr(min_length=3) = ""
    email: EmailStr
    password: constr(min_length=8)
    phone: Optional[str] = ""
    is_authenticated: bool = False
    status: Optional[StatusEnum] = "enabled"
    class Config:
        from_attributes = True

class UserUpdateSchema(BaseModel):
    name: constr(min_length=3) = ""
    phone: Optional[str] = ""
    class Config:
        from_attributes = True

class CreateUserSchema(UserBaseSchema):
    role: str = 'user'
    created_at: datetime = None
    updated_at: datetime = None


class LoginUserSchema(BaseModel):
    email: EmailStr
    password: constr(min_length=8)


class Token(BaseModel):
    access_token: str


class EmailVerificationRequest(BaseModel):
    email: EmailStr