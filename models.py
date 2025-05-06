from sqlalchemy import TIMESTAMP, Column, ForeignKey, Integer, String, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime, timezone
from sqlalchemy.sql import func

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    username = Column(String(20), nullable=False, unique=True, index=True)
    email = Column(String(200), nullable=False, unique=True, index=True)
    password = Column(String(100), nullable=False)
    is_verified = Column(Boolean, default=False, index=True)
    join_date = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())


    # Relationship to the Business table
    businesses = relationship("Business", back_populates="owner")
    
    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}')>"
    






class Business(Base):
    __tablename__ = 'businesses'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    business_name = Column(String(50), nullable=False, index=True)
    city = Column(String(100), nullable=False, server_default="Unspecified")
    region = Column(String(100), nullable=False, server_default="Unspecified")
    business_description = Column(Text, nullable=True)
    logo = Column(String(255), nullable=False, default="default.jpg")  # Path or URL to the logo
    owner_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False, index=True)

    # Relationship to the User table
    owner = relationship("User", back_populates="businesses")

    def __repr__(self):
        return f"<Business(business_name='{self.business_name}', owner_id={self.owner_id})>"





