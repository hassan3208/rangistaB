# models.py
from sqlalchemy import Column, Integer, String, Boolean, Float, Date, ForeignKey, JSON, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

# -------------------------
# USERS TABLE
# -------------------------
class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)  # Changed to str for Supabase UUID
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    disabled = Column(Boolean, default=False)
    contact_number = Column(String, nullable=False) 
    permanent_address = Column(String, nullable=False) 
    country = Column(String, nullable=False) 
    city = Column(String, nullable=False) 
    contact_number_2 = Column(String, nullable=True) 

    # Relationships
    reviews = relationship("Review", back_populates="user", cascade="all, delete")
    carts = relationship("Cart", back_populates="user", cascade="all, delete")
    orders = relationship("Order", back_populates="user", cascade="all, delete")

# -------------------------
# PRODUCTS TABLE
# -------------------------
class Product(Base):
    __tablename__ = "products"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    image = Column(String, nullable=False)
    images = Column(String, nullable=True)  # JSON string
    collection = Column(String, nullable=False)
    category = Column(String, nullable=False)  # New
    discount = Column(Integer, default=0)  # New, 0-100
    colors = Column(String, nullable=True)  # New, JSON string
    description = Column(String, nullable=True)
    XS_price = Column(Integer, nullable=False)
    S_price = Column(Integer, nullable=False)
    M_price = Column(Integer, nullable=False)
    L_price = Column(Integer, nullable=False)
    XL_price = Column(Integer, nullable=False)
    XXL_price = Column(Integer, nullable=False)
    XS_stock = Column(Float, nullable=False)
    S_stock = Column(Float, nullable=False)
    M_stock = Column(Float, nullable=False)
    L_stock = Column(Float, nullable=False)
    XL_stock = Column(Float, nullable=False)
    XXL_stock = Column(Float, nullable=False)
    kids = Column(Boolean, nullable=True)

    # Relationships
    reviews = relationship("Review", back_populates="product", cascade="all, delete")
    carts = relationship("Cart", back_populates="product", cascade="all, delete")
    order_items = relationship("OrderItem", back_populates="product", cascade="all, delete")

# -------------------------
# REVIEWS TABLE
# -------------------------
class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    stars = Column(Float, nullable=False)
    text = Column(String, nullable=True)
    time = Column(Date, nullable=False)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(String, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)

    # Relationships
    user = relationship("User", back_populates="reviews")
    product = relationship("Product", back_populates="reviews")

# -------------------------
# CART TABLE
# -------------------------
class Cart(Base):
    __tablename__ = "cart"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(String, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    size = Column(String(5), nullable=False)  # XS, S, M, L, XL, XXL
    quantity = Column(Integer, default=1, nullable=False)
    color = Column(String, nullable=True)

    # Relationships
    user = relationship("User", back_populates="carts")
    product = relationship("Product", back_populates="carts")

# -------------------------
# ORDERS TABLE
# -------------------------
class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(String, nullable=False)
    time = Column(Date, nullable=False)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Relationships
    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete")

# -------------------------
# ORDER ITEMS TABLE
# -------------------------
class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(String, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    size = Column(String(5), nullable=False)  # XS, S, M, L, XL, XXL
    quantity = Column(Integer, default=1, nullable=False)
    color = Column(String, nullable=True)

    # Relationships
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")