# models.py
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, INTEGER, String, TIMESTAMP, BIGINT, BOOLEAN, text , JSON, DateTime
from sqlalchemy import func

Base = declarative_base()

class Transaction(Base):
    __tablename__ = "transaction"

    id = Column(INTEGER, primary_key=True, index=True)
    fc_transaction_id= Column(String)
    fc_house_id= Column(String)
    grantor= Column(String)
    grantee= Column(String)
    party_company= Column(String)
    cross_party_company= Column(String)
    county= Column(String)
    fc_created_at= Column(String)
    fc_updated_at= Column(String)
    mortgage_maturity_date= Column(String)
    pdf_id= Column(String)
    recorded_date= Column(String)
    signer= Column(String)
    transaction_date= Column(String)
    transaction_number= Column(String)
    transaction_type= Column(String)
    lat= Column(String)
    lng= Column(String)
    fc_10_yr_t_note= Column(String)
    transaction_meta= Column(JSON)
    amount= Column(String)
    address = Column(String)
    pdf = Column(String)
    fc_party_company = Column(String)
    fc_cross_party_company = Column(String)
    state_name = Column(String)
    msa_name = Column(String)
    fip_code = Column(String)


class Company(Base):
    __tablename__ = "company"

    company_id = Column(INTEGER,primary_key=True, index=True)
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
  




class User(Base):
    __tablename__ = 'user'

    id = Column(INTEGER, primary_key=True, autoincrement=True)
    user_name = Column(String)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    role = Column(String, server_default='user', nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    
