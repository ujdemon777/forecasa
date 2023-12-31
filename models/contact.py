# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy import Column, INTEGER, String, DateTime, Enum, ForeignKey
# from sqlalchemy import func
# from sqlalchemy.orm import relationship
# from models.company import Company

# Base = declarative_base()

# class Contact(Base):
#     __tablename__ = 'contact'

#     id = Column(INTEGER, primary_key=True, autoincrement=True)
#     first_name = Column(String)
#     last_name = Column(String)
#     email = Column(String, unique=True, nullable=False)
#     primary_contact = Column(String, nullable=True)
#     secondary_contact = Column(String, nullable=True)
#     linkedIn =  Column(String)
#     contact_type = Column(Enum)
#     created_at = Column(DateTime, default=func.now())
#     company_id = Column(INTEGER, ForeignKey("company.id"))

#     # Company.company = relationship("Company", back_populates="contacts")