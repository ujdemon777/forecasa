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
