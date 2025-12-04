# schemas.py
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import date

# -------------------------
# USER SCHEMAS
# -------------------------
class UserBase(BaseModel):
    name: Optional[str] = None
    username: str
    email: EmailStr
    contact_number: str 
    permanent_address: str 
    country: str 
    city: str 
    contact_number_2: Optional[str] = None

class UserCreate(UserBase):
    pass  # No password anymore

class UserResponse(UserBase):
    id: str
    disabled: bool

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    # email: Optional[EmailStr] = None
    name: Optional[str] = None
    disabled: Optional[bool] = None
    contact_number: Optional[str] = None 
    permanent_address: Optional[str] = None 
    country: Optional[str] = None 
    city: Optional[str] = None 
    contact_number_2: Optional[str] = None

# -------------------------
# PRODUCT & REVIEW SCHEMAS
# -------------------------
class ReviewBase(BaseModel):
    stars: float
    time: str
    user_id: str
    product_id: str

class ReviewResponse(ReviewBase):
    id: int

    class Config:
        from_attributes = True

class ProductBase(BaseModel):
    id: str
    name: str
    image: str
    images: Optional[List[str]] = None
    collection: str
    category: str
    discount: int = 0
    colors: Optional[List[str]] = None
    description: Optional[str] = None

class ProductCreate(ProductBase):
    XS_price: int
    S_price: int
    M_price: int
    L_price: int
    XL_price: int
    XXL_price: int
    XS_stock: float
    S_stock: float
    M_stock: float
    L_stock: float
    XL_stock: float
    XXL_stock: float
    kids: Optional[bool] = None

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    image: Optional[str] = None
    images: Optional[List[str]] = None
    collection: Optional[str] = None
    category: Optional[str] = None
    discount: Optional[int] = None
    colors: Optional[List[str]] = None
    description: Optional[str] = None
    XS_price: Optional[int] = None
    S_price: Optional[int] = None
    M_price: Optional[int] = None
    L_price: Optional[int] = None
    XL_price: Optional[int] = None
    XXL_price: Optional[int] = None
    XS_stock: Optional[float] = None
    S_stock: Optional[float] = None
    M_stock: Optional[float] = None
    L_stock: Optional[float] = None
    XL_stock: Optional[float] = None
    XXL_stock: Optional[float] = None
    kids: Optional[bool] = None

class ProductResponse(ProductBase):
    total_reviews: int
    average_rating: Optional[float] = 0.0
    XS_price: int
    S_price: int
    M_price: int
    L_price: int
    XL_price: int
    XXL_price: int
    XS_stock: float
    S_stock: float
    M_stock: float
    L_stock: float
    XL_stock: float
    XXL_stock: float
    kids: Optional[bool] = None

    class Config:
        from_attributes = True

# -------------------------
# REVIEW SCHEMAS
# -------------------------
class ReviewDetail(BaseModel):
    username: str
    stars: float
    text: Optional[str] = None
    time: date

    class Config:
        from_attributes = True

# -------------------------
# CART RESPONSE SCHEMA
# -------------------------
class CartProduct(BaseModel):
    product_name: str
    collection: str
    size: str
    quantity: int
    image: str
    user_id: str
    product_id: str
    price: int
    color: Optional[str] = None

    class Config:
        from_attributes = True

class CartResponse(BaseModel):
    total_products: int
    items: List[CartProduct]

# -------------------------
# ORDER RESPONSE SCHEMA
# -------------------------
class OrderProduct(BaseModel):
    product_name: str
    quantity: int
    size: str
    product_id: str
    price: int  # Added price field

class OrderResponse(BaseModel):
    order_id: int
    user_id: str  # Changed to str
    username: str
    status: str
    total_products: int
    total_price: int  # Added total_price field
    products: List[OrderProduct]
    order_time: date
    color: Optional[str] = None

    class Config:
        from_attributes = True

# -------------------------
# NEW SCHEMAS
# -------------------------
class ReviewCreate(BaseModel):
    user_id: str
    product_id: str
    stars: float
    text: Optional[str] = None
    time: str

class OrderUpdate(BaseModel):
    status: str

class CartUpdate(BaseModel):
    user_id: str
    product_id: str
    size: str
    quantity: int
    
class CartCreate(BaseModel):
    user_id: str
    product_id: str
    size: str
    quantity: int = 1
    color: Optional[str] = None

# -------------------------
# ORDER CREATE SCHEMA
# -------------------------
class OrderCreate(BaseModel):
    user_id: str
    order_time: str
    
    
class CartRemoveRequest(BaseModel):
    user_id: str
    product_id: str
    size: str
    
    
class ForgotPasswordRequest(BaseModel):
    email: EmailStr
