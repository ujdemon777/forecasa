from pydantic import BaseModel, EmailStr
from typing import Optional
from Enum import ContactEnum


class ContactBaseSchema(BaseModel):
    first_name: Optional[str] = ""
    last_name: Optional[str] = ""
    email: EmailStr
    primary_contact: Optional[str] = ""
    secondary_contact: Optional[str] = ""
    linkedIn: Optional[str] = ""
    contact_type: Optional[ContactEnum] = "primary"

    company_id : int

    class Config:
        from_attributes = True
