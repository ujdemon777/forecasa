from pydantic import BaseModel, EmailStr, constr
from datetime import datetime
from typing import Optional

class UserBaseSchema(BaseModel):
    first_name: Optional[str] = ""
    last_name : Optional[str] = ""
    email: EmailStr
    password: constr(min_length=8)
    phone: Optional[str] = ""

    class Config:
        orm_mode = True

class CreateUserSchema(UserBaseSchema):
    role: str = 'user'
    created_at: datetime = None
    updated_at: datetime = None


class LoginUserSchema(BaseModel):
    email: EmailStr
    password: constr(min_length=8)



class Token(BaseModel):
    access_token: str
    token_type: str


class DataToken(BaseModel):
    id: Optional[str] = None