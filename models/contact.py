from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, INTEGER, String, DateTime, Enum
from sqlalchemy import func

Base = declarative_base()

class Contact(Base):
    __tablename__ = 'contact'

    id = Column(INTEGER, primary_key=True, autoincrement=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True, nullable=False)
    primary_contact = Column(String, nullable=True)
    secondary_contact = Column(String, nullable=True)
    linkedin =  Column(String)
    contact_type = Column(Enum)
    created_at = Column(DateTime, default=func.now())