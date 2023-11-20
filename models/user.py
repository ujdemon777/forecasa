from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, INTEGER, String, TIMESTAMP, BIGINT, Boolean, text , JSON, DateTime
from sqlalchemy import func

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'

    id = Column(INTEGER, primary_key=True, autoincrement=True)
    user_name = Column(String)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    role = Column(String, server_default='user', nullable=False)
    is_authenticated =Column(Boolean(), default=False)
    status = Column(String,nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())