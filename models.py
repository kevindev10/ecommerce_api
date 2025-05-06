from sqlalchemy import TIMESTAMP, Column, ForeignKey, Integer, String, Boolean, DateTime, Text, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime, timezone, timedelta
from sqlalchemy.sql import func, text

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

    # Relationship to the Product table
    products = relationship("Product", back_populates="business")

    def __repr__(self):
        return f"<Business(business_name='{self.business_name}', owner_id={self.owner_id})>"







class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    category = Column(String(50), nullable=False, index=True)
    original_price = Column(Numeric(12, 2))
    new_price = Column(Numeric(12, 2))
    percentage_discount = Column(Integer)
    offer_expiration_date = Column(DateTime, nullable=False, server_default=text("(CURRENT_TIMESTAMP + interval '30 days')"))
    product_image = Column(String(255), nullable=False, default="productDefault.jpg")  # Path or URL to the product image
    business_id = Column(Integer, ForeignKey('businesses.id', ondelete="CASCADE"), nullable=False, index=True)

    # Relationship to the Business table
    business = relationship("Business", back_populates="products")

    def __repr__(self):
        return f"<Product(name='{self.name}', category='{self.category}', business_id={self.business_id})>"






# @property
# def calculated_discount(self):
#     if self.original_price and self.new_price:
#         return round(((self.original_price - self.new_price) / self.original_price) * 100, 2)
#     return None
