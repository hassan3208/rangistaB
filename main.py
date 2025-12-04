from fastapi import FastAPI, Depends, HTTPException, status, Query, Request, Response, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Annotated, List, Optional 
from datetime import timedelta
from fastapi.middleware.cors import CORSMiddleware
import models, schemas, crud, database
from email_func import send_welcome
import logging
import json
from sqlalchemy.exc import OperationalError
from jose import jwt, JWTError
from auth import get_current_user  # New auth
from typing import Annotated
import auth
from dotenv import load_dotenv
import os
import requests

load_dotenv()

SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE = os.getenv("SUPABASE_SERVICE_ROLE")

# Custom auth dependency that handles both JWT and simple user ID tokens
def verify_token(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())) -> str:
    """
    Flexible token verification - handles both JWT tokens and simple user IDs for testing
    """
    token = credentials.credentials
    
    # First try to decode as JWT
    try:
        payload = jwt.decode(token, SUPABASE_JWT_SECRET, algorithms=[ALGORITHM], audience="authenticated")
        return payload.get("sub")  # Return user ID from JWT
    except JWTError:
        # If JWT decode fails, treat as simple user ID for testing
        # In production, you should remove this fallback
        if token and len(token) > 10:  # Basic validation for user ID format
            return token
        raise HTTPException(status_code=401, detail="Invalid token format")

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

models.Base.metadata.create_all(bind=database.engine)

origins = [
    "http://localhost:8080",
    "http://127.0.0.1:8000",
    "https://rangista.vercel.app",
    "https://rangistawebsite.vercel.app",
]

app = FastAPI(title='User Management API')

bearer_scheme = HTTPBearer()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/test-token")
def get_test_token():
    """
    Sirf testing ke liye - ek valid Supabase JWT deta hai
    Frontend aane ke baad delete kar dena ya comment kar dena
    """
    import jwt
    from datetime import datetime, timedelta

    payload = {
        "sub": "test-user-123",           # ← ye user_id use hoga sab jagah
        "email": "test@rangista.com",
        "aud": "authenticated",
        "role": "authenticated",
        "exp": datetime.utcnow() + timedelta(hours=24),
        "iat": datetime.utcnow(),
    }
    token = jwt.encode(payload, SUPABASE_JWT_SECRET, algorithm=ALGORITHM)
    return {"access_token": token}

# -------------------------
# CREATE USER PROFILE (called by frontend after Supabase signup)
# -------------------------
@app.post("/profiles", response_model=schemas.UserResponse)
async def create_profile(
    user: schemas.UserCreate,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    db: Session = Depends(database.get_db)
):
    # Use the flexible token verification
    supabase_user_id = verify_token(credentials)
    
    # For JWT tokens, also verify email match
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SUPABASE_JWT_SECRET, algorithms=[ALGORITHM], audience="authenticated")
        email_from_token: str = payload.get("email")
        if email_from_token and user.email != email_from_token:
            raise HTTPException(status_code=401, detail="Token/email mismatch")
    except JWTError:
        # Skip email verification for simple user ID tokens
        pass

    # Baki sab same rahega...
    if crud.get_user_by_username(db, user.username):
        raise HTTPException(status_code=400, detail="Username already registered")
    if crud.get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    created_user = crud.create_user(db, user, supabase_user_id)
    send_welcome(to_email=created_user.email, to_name=created_user.name or "there")
    return created_user



# -------------------------
# FORGOT PASSWORD
# -------------------------
@app.post("/auth/forgot-password")
def forgot_password(request: schemas.ForgotPasswordRequest, db: Session = Depends(database.get_db)):

    user = crud.get_user_by_email(db, request.email)
    if not user:
        raise HTTPException(status_code=404, detail="Email not found")

    # Supabase Password Reset API
    reset_url = f"{SUPABASE_URL}/auth/v1/recover"

    res = requests.post(
        reset_url,
        json={"email": request.email},
        headers={
            "apikey": SUPABASE_SERVICE_ROLE,
            "Content-Type": "application/json"
        }
    )

    if res.status_code not in [200, 204]:
        raise HTTPException(status_code=500, detail="Failed to send reset email")

    return {"message": "Password reset email sent successfully"}



# -------------------------
# GET ALL USERS (no auth for now, add if needed)
# -------------------------
@app.get("/users", response_model=List[schemas.UserResponse])
def get_users(db: Session = Depends(database.get_db)):
    users = crud.get_all_users(db)
    return users

# -------------------------
# GET USER BY ID (no auth for now)
# -------------------------
@app.get("/users/{user_id}", response_model=schemas.UserResponse)
def get_user(
    user_id: str,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)], 
    db: Session = Depends(database.get_db)
):
    # Verify token but don't require user match for this endpoint
    verify_token(credentials)
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# -------------------------
# UPDATE USER
# -------------------------
@app.put("/users/{user_id}", response_model=schemas.UserResponse)
def update_user(
    user_id: str, 
    user_update: schemas.UserUpdate, 
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    db: Session = Depends(database.get_db)
):
    # Verify token and check user match
    token_user_id = verify_token(credentials)
    if token_user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    db_user = crud.get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.update_user(db, db_user, user_update)

# -------------------------
# GET ALL PRODUCTS
# -------------------------
@app.get("/products", response_model=List[schemas.ProductResponse])
def get_all_products(db: Session = Depends(database.get_db)):
    return crud.get_all_products_with_reviews(db)


#-------------------------
# GET PRODUCT BY ID
#-------------------------

@app.get("/product/{product_id}", response_model=schemas.ProductResponse)
def get_product_by_id(product_id: str, db: Session = Depends(database.get_db)):
    """
    get a complete product just by adding ID
    """
    product = crud.get_product_with_reviews(db=db, product_id=product_id)
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return product



# -------------------------
# CREATE PRODUCT
# -------------------------
@app.post("/products", response_model=schemas.ProductResponse)
def create_product(product: schemas.ProductCreate, db: Session = Depends(database.get_db)):
    db_product = crud.get_product_by_id(db, product.id)
    if db_product:
        raise HTTPException(status_code=400, detail="Product ID already exists")
    
    try:
        crud.create_product(db, product)
        new_product = crud.get_product_with_reviews(db, product.id)
        if not new_product:
            raise HTTPException(status_code=500, detail="Failed to retrieve created product")
        return new_product
    except OperationalError as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=503, detail="Database unavailable, please try again later")
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error for images field: {str(e)}")
        raise HTTPException(status_code=500, detail="Error processing product images")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# -------------------------
# DELETE PRODUCT (NEW)
# -------------------------
@app.delete("/products/{product_id}")
def delete_product(product_id: str, db: Session = Depends(database.get_db)):
    deleted = crud.delete_product(db, product_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted successfully"}

# -------------------------
# UPDATE PRODUCT (NEW)
# -------------------------
@app.put("/products/{product_id}", response_model=schemas.ProductResponse)
def update_product(product_id: str, product_update: schemas.ProductUpdate, db: Session = Depends(database.get_db)):
    updated = crud.update_product(db, product_id, product_update)
    if not updated:
        raise HTTPException(status_code=404, detail="Product not found")
    return crud.get_product_with_reviews(db, product_id)

# -------------------------
# GET ALL REVIEWS FOR A PRODUCT
# -------------------------
@app.get("/products/{product_id}/reviews", response_model=list[schemas.ReviewDetail])
def get_product_reviews(product_id: str, db: Session = Depends(database.get_db)):
    reviews = crud.get_reviews_by_product(db, product_id)
    if not reviews:
        raise HTTPException(status_code=404, detail="No reviews found for this product.")
    return reviews

# -------------------------
# GET USER CART ENDPOINT
# -------------------------
@app.get("/cart/{user_id}", response_model=schemas.CartResponse)
def get_user_cart(
    user_id: str,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    db: Session = Depends(database.get_db)
):
    token_user_id = verify_token(credentials)
    if token_user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    cart_data = crud.get_user_cart(db, user_id)
    if not cart_data.items:
        raise HTTPException(status_code=404, detail="No items found in cart")
    return cart_data

# -------------------------
# GET ALL ORDERS
# -------------------------
@app.get("/orders", response_model=List[schemas.OrderResponse])
def read_all_orders(db: Session = Depends(database.get_db)):
    orders = crud.get_all_orders(db)
    if not orders:
        raise HTTPException(status_code=404, detail="No orders found")
    return orders

# -------------------------
# GET ALL ORDERS OF A USER
# -------------------------
@app.get("/users/{user_id}/orders", response_model=List[schemas.OrderResponse])
def read_user_orders(
    user_id: str, 
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)], 
    db: Session = Depends(database.get_db)
):
    token_user_id = verify_token(credentials)
    if token_user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    orders = crud.get_user_orders(db, user_id)
    if not orders:
        raise HTTPException(status_code=404, detail="No orders found for this user")
    return orders

# -------------------------
# UPDATE ORDER STATUS
# -------------------------
@app.put("/orders/{order_id}/status", response_model=schemas.OrderResponse)
def update_order_status(order_id: int, update: schemas.OrderUpdate, db: Session = Depends(database.get_db)):
    order = crud.update_order_status(db, order_id, update.status)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return crud.get_order(db, order_id)

# -------------------------
# CREATE REVIEW
# -------------------------
@app.post("/reviews/", response_model=schemas.ReviewDetail)
def create_product_review(
    review: schemas.ReviewCreate, 
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)], 
    db: Session = Depends(database.get_db)
):
    token_user_id = verify_token(credentials)
    if token_user_id != review.user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    db_review = crud.create_review(db, review)
    if not db_review:
        raise HTTPException(status_code=400, detail="Could not create review")
    return crud.get_review_detail(db, db_review.id)

# -------------------------
# UPDATE CART QUANTITY
# -------------------------
# NEW: UPDATE CART ITEM (quantity or remove if 0)
@app.put("/cart/update", response_model=schemas.CartResponse)
def update_cart_item(
    payload: schemas.CartUpdate,                           # ← This is now a Pydantic model
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    db: Session = Depends(database.get_db)
):
    token_user_id = verify_token(credentials)
    if token_user_id != payload.user_id:                  # ← Use payload.user_id (not .get())
        raise HTTPException(status_code=403, detail="Not authorized")

    if payload.quantity <= 0:
        success = crud.remove_from_cart(db, payload.user_id, payload.product_id, payload.size)
    else:
        success = crud.update_cart_quantity(db, payload.user_id, payload.product_id, payload.size, payload.quantity)

    if not success:
        raise HTTPException(status_code=404, detail="Cart item not found")

    return crud.get_user_cart(db, payload.user_id)

# -------------------------
# REMOVE FROM CART
# -------------------------
@app.delete("/cart/remove", response_model=schemas.CartResponse)
def remove_cart_item(
    remove_data: schemas.CartRemoveRequest,  # { "user_id", "product_id", "size" }
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    db: Session = Depends(database.get_db)
):
    token_user_id = verify_token(credentials)
    user_id = remove_data.user_id
    product_id = remove_data.product_id
    size = remove_data.size

    if not all([user_id, product_id, size]):
        raise HTTPException(status_code=400, detail="Missing required fields")

    if token_user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    success = crud.remove_from_cart(db, user_id, product_id, size)
    if not success:
        raise HTTPException(status_code=404, detail="Cart item not found")

    return crud.get_user_cart(db, user_id)

# -------------------------
# ADD TO CART
# -------------------------
@app.post("/cart/", response_model=schemas.CartResponse)
def add_to_cart(
    cart_item: schemas.CartCreate, 
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)], 
    db: Session = Depends(database.get_db)
):
    token_user_id = verify_token(credentials)
    if token_user_id != cart_item.user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    
    product = crud.get_product_by_id(db, cart_item.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product ID does not exist")
    
    added = crud.add_to_cart(db, cart_item)
    if not added:
        raise HTTPException(status_code=400, detail="Could not add item to cart")
    return crud.get_user_cart(db, cart_item.user_id)

# -------------------------
# CREATE ORDER FROM CART
# -------------------------
@app.post("/orders/from-cart/", response_model=List[schemas.OrderResponse])
def create_order_from_cart(
    order: schemas.OrderCreate, 
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)], 
    db: Session = Depends(database.get_db)
):
    token_user_id = verify_token(credentials)
    if token_user_id != order.user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    orders = crud.create_order_from_cart(db, order)
    if not orders:
        raise HTTPException(status_code=400, detail="Could not create order")
    return orders

@app.get("/reviews/check")
def check_review(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    user_id: str = Query(...),
    order_id: int = Query(...),
    product_id: str = Query(...),
    size: Optional[str] = Query(None),
    db: Session = Depends(database.get_db)
):
    token_user_id = verify_token(credentials)
    if token_user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    reviewed = crud.has_user_reviewed_product(db, user_id, product_id)
    return {"reviewed": reviewed}

# -------------------------
# GET PRODUCT DESCRIPTION
# -------------------------
@app.get("/products/{product_id}/description")
def get_product_description(product_id: str, db: Session = Depends(database.get_db)):
    db_product = crud.get_product_by_id(db, product_id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"description": db_product.description or ""}

@app.get("/")
def read_root():
    return {"message": "Server is running!"}










