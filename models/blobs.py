# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy import Column, INTEGER, ForeignKey, String, TIMESTAMP, BIGINT, Boolean, text , JSON, DateTime 
# from sqlalchemy import func
# from sqlalchemy.orm import relationship

# Base = declarative_base()

# class Blob(Base):
#     __tablename__ = 'blobs'

#     id = Column(INTEGER, primary_key=True, autoincrement=True)
#     created_at = Column(DateTime, default=func.now())
#     updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
#     file_name = Column(String , unique=True, nullable=False)
#     source = Column(String , nullable=False)
#     meta_data = Column(JSON , nullable=False)
#     status = Column(String,nullable=False)
#     project_label = Column(String,nullable=False)
#     user_id = Column(INTEGER, ForeignKey("user.id"))

#     users = relationship("User", back_populates="blobs")