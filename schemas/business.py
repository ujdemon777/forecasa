from pydantic import BaseModel, EmailStr
from typing import Optional
from Enum import ContactEnum
from datetime import datetime

class BusinessBaseSchema(BaseModel):
    business_id: int
    source: str
    api_key: str
    fernet_key: Optional[bytes] = None
    created_at: datetime = None
    updated_at: datetime = None

    class Config:
        from_attributes = True

class UpdateBusinessBaseSchema(BaseModel):
    business_id: int
    source: Optional[str] = None
    api_key: Optional[str] = None
    fernet_key: Optional[bytes] = None

    class Config:
        from_attributes = True
