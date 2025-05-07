from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List, Optional

# -------------------- User Schemas --------------------
class UserBase(BaseModel):
    username: str
    email: EmailStr

    class Config:
        orm_mode = True


class UserCreate(UserBase):
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    join_date: datetime  # No default—handled at the database level

    class Config:
        orm_mode = True
        fields = {"is_verified": {"exclude": True}}  # Excluding is_verified


# -------------------- Product Schemas --------------------
class ProductResponse(BaseModel):
    name: str
    category: str
    original_price: float
    new_price: Optional[float]
    offer_expiration_date: datetime
    product_image: str
    business_id: int  

    class Config:
        orm_mode = True
        fields = {
            "business_id": {"exclude": True},  
            "percentage_discount": {"exclude": True},  # Excluding percentage_discount
            "id": {"exclude": True}  # Excluding product ID
        }


# -------------------- Business Schemas --------------------
class BusinessResponse(BaseModel):
    id: int
    business_name: str
    city: str
    region: str
    business_description: Optional[str]
    logo: str
    owner: UserOut  
    products: Optional[List[ProductResponse]] = []  
    owner_id: int  

    class Config:
        orm_mode = True
        fields = {"owner_id": {"exclude": True}}  # Excluding owner_id


class BusinessIn(BaseModel):
    business_name: str
    city: str
    region: str
    business_description: Optional[str]
    logo: str
    owner_id: int  

    class Config:
        orm_mode = True


# -------------------- Product Schemas (Creation) --------------------
class ProductIn(BaseModel):
    name: str
    category: str
    original_price: float
    new_price: Optional[float]
    offer_expiration_date: datetime
    product_image: str
    business_id: int  

    class Config:
        orm_mode = True
