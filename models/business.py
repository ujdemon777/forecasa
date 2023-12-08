from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, INTEGER, LargeBinary, String, TIMESTAMP, BIGINT, Boolean, text , JSON, DateTime
from sqlalchemy import func

Base = declarative_base()

class Business(Base):
    __tablename__ = 'business_credential'

    id = Column(INTEGER, primary_key=True, autoincrement=True)
    business_id = Column(INTEGER)
    source = Column(String, nullable=False)
    api_key = Column(LargeBinary(100), nullable=False)
    fernet_key = Column(LargeBinary(100), nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    api_last_four = Column(String, nullable=False)