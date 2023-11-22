from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, INTEGER, String, TIMESTAMP, BIGINT, BOOLEAN, text , JSON, DateTime
from sqlalchemy import func
from sqlalchemy.orm import relationship

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
    last_lender_used = Column(String)
    other_lenders_used = Column(String)
    last_mortgage_date = Column(String)
    last_transaction_date = Column(String)
    mortgage_transactions = Column(INTEGER)
    party_count = Column(INTEGER)
    satisfaction_of_mortgage_transactions= Column(INTEGER)
    transactions_as_borrower = Column(INTEGER)
    transactions_as_buyer = Column(INTEGER)
    transactions_as_lender = Column(INTEGER)
    transactions_as_seller = Column(INTEGER)
    last_county = Column(String)
    principal_address = Column(String)
    principal_name = Column(String)
    average_mortgage_amount = Column(INTEGER)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # contacts = relationship("Contact", back_populates="owner")