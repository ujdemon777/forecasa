from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, INTEGER, String, TIMESTAMP, BIGINT, BOOLEAN, text , JSON, DateTime,Enum,ForeignKey
from sqlalchemy import func
from sqlalchemy.orm import relationship

# from models.contact import Contact

Base = declarative_base()

class Company(Base):
    __tablename__ = "company"

    id = Column(INTEGER,primary_key=True, index=True)
    name = Column(String)
    dba = Column(JSON)
    tag_names = Column(JSON)
    leads = Column(String)
    assignment_of_mortgage_transactions = Column(INTEGER)
    deed_transactions = Column(INTEGER)
    last_lender_used = Column(String,index=True)
    other_lenders_used = Column(String)
    last_mortgage_date = Column(String,index=True)
    last_transaction_date = Column(String,index=True)
    mortgage_transactions = Column(INTEGER,index=True)
    party_count = Column(INTEGER)
    satisfaction_of_mortgage_transactions= Column(INTEGER)
    transactions_as_borrower = Column(INTEGER)
    transactions_as_buyer = Column(INTEGER)
    transactions_as_lender = Column(INTEGER)
    transactions_as_seller = Column(INTEGER)
    last_county = Column(String)
    principal_address = Column(String)
    principal_name = Column(String)
    average_mortgage_amount = Column(INTEGER,index=True)
    created_at = Column(DateTime, default=func.now(),index=True)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    contacts = relationship("Contact", back_populates="company")



class Contact(Base):
    __tablename__ = 'contact'

    id = Column(INTEGER, primary_key=True, autoincrement=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, nullable=False)
    primary_contact = Column(String, nullable=True)
    secondary_contact = Column(String, nullable=True)
    linkedIn =  Column(String)
    created_at = Column(DateTime, default=func.now())
    company_id = Column(INTEGER, ForeignKey("company.id"))

    company = relationship("Company", back_populates="contacts")