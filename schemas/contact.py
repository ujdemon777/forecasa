from pydantic import BaseModel, EmailStr
from typing import Optional
from Enum import ContactEnum
from datetime import datetime

class ContactBaseSchema(BaseModel):
    first_name: Optional[str] = ""
    last_name: Optional[str] = ""
    email: EmailStr
    primary_contact: Optional[str] = ""
    secondary_contact: Optional[str] = ""
    linkedIn: Optional[str] = ""
    created_at: datetime = None
    contact_type : ContactEnum = "primary"
    company_id : int

    class Config:
        from_attributes = True
