from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import INTEGER, Column,String

Base = declarative_base()

class Leads(Base):
    __tablename__ = 'leads'

    company_key = Column(String, primary_key=True)
    status = Column(String, nullable=False)
    company_id = Column(INTEGER)
    company_name = Column(String) 