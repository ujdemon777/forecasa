from pydantic import BaseModel, EmailStr, constr
from datetime import datetime
from typing import Optional

class UserBaseSchema(BaseModel):
    user_name: Optional[str] = ""
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




class CompanyFilters(BaseModel):
    child_sponsor: Optional[str] = None
    transaction_type: Optional[list] = None
    transaction_tags: Optional[list] = None
    counties: Optional[list] = None
    amount: Optional[dict]= None