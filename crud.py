# crud.py
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, case, and_
from datetime import date
from typing import Optional, List
import models, schemas
import json
from fastapi import HTTPException

# -------------------------
# USER FUNCTIONS
# -------------------------
def get_user_by_id(db: Session, user_id: str):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_all_users(db: Session):
    return db.query(models.User).all()

def create_user(db: Session, user: schemas.UserCreate, user_id: str):
    db_user = models.User(
        id=user_id,
        name=user.name or "",
        username=user.username,
        email=user.email,
        disabled=False,
        contact_number=user.contact_number,
        permanent_address=user.permanent_address,
        country=user.country,
        city=user.city,
        contact_number_2=user.contact_number_2
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, db_user: models.User, updates: schemas.UserUpdate):
    # if updates.email is not None:
    #     db_user.email = updates.email
    if updates.name is not None:
        db_user.name = updates.name
    if updates.disabled is not None:
        db_user.disabled = updates.disabled
    if updates.contact_number is not None:
        db_user.contact_number = updates.contact_number
    if updates.permanent_address is not None:
        db_user.permanent_address = updates.permanent_address
    if updates.country is not None:
        db_user.country = updates.country
    if updates.city is not None:
        db_user.city = updates.city
    if updates.contact_number_2 is not None:
        db_user.contact_number_2 = updates.contact_number_2
    db.commit()
    db.refresh(db_user)
    return db_user

# -------------------------
# PRODUCT FUNCTIONS
# -------------------------
def get_all_products_with_reviews(db: Session):
    results = (
        db.query(
            models.Product.id,
            models.Product.name,
            models.Product.image,
            models.Product.images,
            models.Product.collection,
            models.Product.category,
            models.Product.discount,
            models.Product.colors,
            func.count(models.Review.id).label("total_reviews"),
            func.coalesce(func.avg(models.Review.stars), 0).label("average_rating"),
            models.Product.XS_price,
            models.Product.S_price,
            models.Product.M_price,
            models.Product.L_price,
            models.Product.XL_price,
            models.Product.XXL_price,
            models.Product.XS_stock,
            models.Product.S_stock,
            models.Product.M_stock,
            models.Product.L_stock,
            models.Product.XL_stock,
            models.Product.XXL_stock,
            models.Product.kids,
            models.Product.description,
        )
        .outerjoin(models.Review, models.Product.id == models.Review.product_id)
        .group_by(models.Product.id)
        .all()
    )

    products = []
    for r in results:
        images = json.loads(r.images) if r.images else None
        colors = json.loads(r.colors) if r.colors else None

        products.append(
            schemas.ProductResponse(
                id=r.id,
                name=r.name,
                image=r.image,
                images=images,
                collection=r.collection,
                category=r.category,
                discount=r.discount or 0,
                colors=colors,
                total_reviews=r.total_reviews,
                average_rating=round(float(r.average_rating or 0), 2),
                XS_price=r.XS_price,
                S_price=r.S_price,
                M_price=r.M_price,
                L_price=r.L_price,
                XL_price=r.XL_price,
                XXL_price=r.XXL_price,
                XS_stock=r.XS_stock,
                S_stock=r.S_stock,
                M_stock=r.M_stock,
                L_stock=r.L_stock,
                XL_stock=r.XL_stock,
                XXL_stock=r.XXL_stock,
                kids=r.kids,
                description=r.description,
            )
        )
    return products


def get_product_by_id(db: Session, product_id: str):
    return db.query(models.Product).filter(models.Product.id == product_id).first()


def get_product_with_reviews(db: Session, product_id: str):
    result = (
        db.query(
            models.Product.id,
            models.Product.name,
            models.Product.image,
            models.Product.images,
            models.Product.collection,
            models.Product.category,
            models.Product.discount,
            models.Product.colors,
            func.count(models.Review.id).label("total_reviews"),
            func.coalesce(func.avg(models.Review.stars), 0).label("average_rating"),
            models.Product.XS_price,
            models.Product.S_price,
            models.Product.M_price,
            models.Product.L_price,
            models.Product.XL_price,
            models.Product.XXL_price,
            models.Product.XS_stock,
            models.Product.S_stock,
            models.Product.M_stock,
            models.Product.L_stock,
            models.Product.XL_stock,
            models.Product.XXL_stock,
            models.Product.kids,
            models.Product.description,
        )
        .outerjoin(models.Review, models.Product.id == models.Review.product_id)
        .filter(models.Product.id == product_id)
        .group_by(models.Product.id)
        .first()
    )
    if not result:
        return None

    images = json.loads(result.images) if result.images else None
    colors = json.loads(result.colors) if result.colors else None

    return schemas.ProductResponse(
        id=result.id,
        name=result.name,
        image=result.image,
        images=images,
        collection=result.collection,
        category=result.category,
        discount=result.discount or 0,
        colors=colors,
        total_reviews=result.total_reviews,
        average_rating=round(float(result.average_rating or 0), 2),
        XS_price=result.XS_price,
        S_price=result.S_price,
        M_price=result.M_price,
        L_price=result.L_price,
        XL_price=result.XL_price,
        XXL_price=result.XXL_price,
        XS_stock=result.XS_stock,
        S_stock=result.S_stock,
        M_stock=result.M_stock,
        L_stock=result.L_stock,
        XL_stock=result.XL_stock,
        XXL_stock=result.XXL_stock,
        kids=result.kids,
        description=result.description,
    )


def create_product(db: Session, product: schemas.ProductCreate):
    db_product = models.Product(
        id=product.id,
        name=product.name,
        image=product.image,
        images=json.dumps(product.images) if product.images else None,
        collection=product.collection,
        category=product.category,
        discount=product.discount,
        colors=json.dumps(product.colors) if product.colors else None,
        XS_price=product.XS_price,
        S_price=product.S_price,
        M_price=product.M_price,
        L_price=product.L_price,
        XL_price=product.XL_price,
        XXL_price=product.XXL_price,
        XS_stock=product.XS_stock,
        S_stock=product.S_stock,
        M_stock=product.M_stock,
        L_stock=product.L_stock,
        XL_stock=product.XL_stock,
        XXL_stock=product.XXL_stock,
        kids=product.kids,
        description=product.description,
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def update_product(db: Session, product_id: str, updates: schemas.ProductUpdate):
    product = get_product_by_id(db, product_id)
    if not product:
        return None

    if updates.name is not None:
        product.name = updates.name
    if updates.image is not None:
        product.image = updates.image
    if updates.images is not None:
        product.images = json.dumps(updates.images)
    if updates.collection is not None:
        product.collection = updates.collection
    if updates.category is not None:
        product.category = updates.category
    if updates.discount is not None:
        product.discount = updates.discount
    if updates.colors is not None:
        product.colors = json.dumps(updates.colors)
    if updates.description is not None:
        product.description = updates.description
    if updates.XS_price is not None:
        product.XS_price = updates.XS_price
    if updates.S_price is not None:
        product.S_price = updates.S_price
    if updates.M_price is not None:
        product.M_price = updates.M_price
    if updates.L_price is not None:
        product.L_price = updates.L_price
    if updates.XL_price is not None:
        product.XL_price = updates.XL_price
    if updates.XXL_price is not None:
        product.XXL_price = updates.XXL_price
    if updates.XS_stock is not None:
        product.XS_stock = updates.XS_stock
    if updates.S_stock is not None:
        product.S_stock = updates.S_stock
    if updates.M_stock is not None:
        product.M_stock = updates.M_stock
    if updates.L_stock is not None:
        product.L_stock = updates.L_stock
    if updates.XL_stock is not None:
        product.XL_stock = updates.XL_stock
    if updates.XXL_stock is not None:
        product.XXL_stock = updates.XXL_stock
    if updates.kids is not None:
        product.kids = updates.kids

    db.commit()
    db.refresh(product)
    return product


def delete_product(db: Session, product_id: str):
    product = get_product_by_id(db, product_id)
    if not product:
        return False
    db.delete(product)
    db.commit()
    return True


# -------------------------
# REVIEW FUNCTIONS
# -------------------------
def get_reviews_by_product(db: Session, product_id: str):
    return (
        db.query(
            models.User.username,
            models.Review.stars,
            models.Review.text,
            models.Review.time,
        )
        .join(models.User, models.Review.user_id == models.User.id)
        .filter(models.Review.product_id == product_id)
        .all()
    )

def create_review(db: Session, review: schemas.ReviewCreate):
    db_review = models.Review(
        stars=review.stars,
        text=review.text,
        time=datetime.fromisoformat(review.time.replace("Z", "+00:00")).date(),
        user_id=review.user_id,
        product_id=review.product_id
    )
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review

def get_review_detail(db: Session, review_id: int):
    review = db.query(models.Review).filter(models.Review.id == review_id).first()
    if not review:
        return None
    user = db.query(models.User).filter(models.User.id == review.user_id).first()
    return schemas.ReviewDetail(
        username=user.username,
        stars=review.stars,
        text=review.text,
        time=review.time
    )

def has_user_reviewed_product(db: Session, user_id: str, product_id: str):
    review = db.query(models.Review).filter(
        models.Review.user_id == user_id,
        models.Review.product_id == product_id
    ).first()
    return review is not None


# -------------------------
# CART FUNCTIONS
# -------------------------
def get_user_cart(db: Session, user_id: str):
    items = (
        db.query(
            models.Cart,
            models.Product.name.label("product_name"),
            models.Product.image,
            models.Product.collection,
            case(
                (models.Cart.size == "XS", models.Product.XS_price),
                (models.Cart.size == "S", models.Product.S_price),
                (models.Cart.size == "M", models.Product.M_price),
                (models.Cart.size == "L", models.Product.L_price),
                (models.Cart.size == "XL", models.Product.XL_price),
                (models.Cart.size == "XXL", models.Product.XXL_price),
                else_=0
            ).label("price")
        )
        .join(models.Product, models.Cart.product_id == models.Product.id)
        .filter(models.Cart.user_id == user_id)
        .all()
    )

    cart_items = [
        schemas.CartProduct(
            product_name=item.product_name,
            collection=item.collection,
            size=item.Cart.size,
            quantity=item.Cart.quantity,
            image=item.image,
            user_id=user_id,
            product_id=item.Cart.product_id,
            price=item.price
        ) for item in items
    ]

    return schemas.CartResponse(
        total_products=len(cart_items),
        items=cart_items
    )

def add_to_cart(db: Session, cart_item: schemas.CartCreate):
    existing = db.query(models.Cart).filter(
        models.Cart.user_id == cart_item.user_id,
        models.Cart.product_id == cart_item.product_id,
        models.Cart.size == cart_item.size
    ).first()

    if existing:
        existing.quantity += cart_item.quantity
    else:
        new_item = models.Cart(
            user_id=cart_item.user_id,
            product_id=cart_item.product_id,
            size=cart_item.size,
            quantity=cart_item.quantity,
            color=cart_item.color
        )
        db.add(new_item)
    db.commit()
    return True

def update_cart_quantity(db: Session, user_id: str, product_id: str, size: str, quantity: int):
    item = db.query(models.Cart).filter(
        models.Cart.user_id == user_id,
        models.Cart.product_id == product_id,
        models.Cart.size == size
    ).first()
    if not item:
        return False
    if quantity <= 0:
        db.delete(item)
    else:
        item.quantity = quantity
    db.commit()
    return True

def remove_from_cart(db: Session, user_id: str, product_id: str, size: str):
    item = db.query(models.Cart).filter(
        models.Cart.user_id == user_id,
        models.Cart.product_id == product_id,
        models.Cart.size == size
    ).first()
    if not item:
        return False
    db.delete(item)
    db.commit()
    return True


# -------------------------
# ORDER FUNCTIONS
# -------------------------
def get_all_orders(db: Session):
    # Fetch summarized order data
    raw_orders = (
        db.query(
            models.Order.id.label("order_id"),
            models.Order.user_id,
            models.User.username,
            models.Order.status,
            func.count(models.OrderItem.id).label("total_products"),
            func.sum(
                models.OrderItem.quantity * case(
                    (models.OrderItem.size == "XS", models.Product.XS_price),
                    (models.OrderItem.size == "S", models.Product.S_price),
                    (models.OrderItem.size == "M", models.Product.M_price),
                    (models.OrderItem.size == "L", models.Product.L_price),
                    (models.OrderItem.size == "XL", models.Product.XL_price),
                    (models.OrderItem.size == "XXL", models.Product.XXL_price),
                    else_=0
                )
            ).label("total_price"),
            models.Order.time.label("order_time")
        )
        .join(models.User, models.Order.user_id == models.User.id)
        .join(models.OrderItem, models.Order.id == models.OrderItem.order_id)
        .join(models.Product, models.OrderItem.product_id == models.Product.id)
        .group_by(models.Order.id, models.User.username)
        .all()
    )

    final_results = []

    for order in raw_orders:
        # Fetch all products inside each order
        order_items = (
            db.query(
                models.OrderItem.product_id,
                models.OrderItem.quantity,
                models.OrderItem.size,
                models.Product.name.label("product_name"),
                models.Product.XS_price,
                models.Product.S_price,
                models.Product.M_price,
                models.Product.L_price,
                models.Product.XL_price,
                models.Product.XXL_price,
            )
            .join(models.Product, models.OrderItem.product_id == models.Product.id)
            .filter(models.OrderItem.order_id == order.order_id)
            .all()
        )

        # Build product list for this order
        products = []
        for item in order_items:
            unit_price = (
                item.XS_price if item.size == "XS" else
                item.S_price if item.size == "S" else
                item.M_price if item.size == "M" else
                item.L_price if item.size == "L" else
                item.XL_price if item.size == "XL" else
                item.XXL_price
            )

            products.append(
                schemas.OrderProduct(
                    product_id=item.product_id,
                    product_name=item.product_name,
                    quantity=item.quantity,
                    size=item.size,
                    price=unit_price * item.quantity
                )
            )

        # Convert into schema output
        final_results.append(
            schemas.OrderResponse(
                order_id=order.order_id,
                user_id=order.user_id,
                username=order.username,
                status=order.status,
                total_products=order.total_products,
                total_price=int(order.total_price or 0),
                order_time=order.order_time,
                products=products
            )
        )

    return final_results

def get_user_orders(db: Session, user_id: str):
    results = (
        db.query(
            models.Order.id.label("order_id"),
            models.Order.user_id,
            models.User.username,
            models.Order.status,
            func.count(models.OrderItem.id).label("total_products"),
            func.sum(
                models.OrderItem.quantity * case(
                    (models.OrderItem.size == "XS", models.Product.XS_price),
                    (models.OrderItem.size == "S", models.Product.S_price),
                    (models.OrderItem.size == "M", models.Product.M_price),
                    (models.OrderItem.size == "L", models.Product.L_price),
                    (models.OrderItem.size == "XL", models.Product.XL_price),
                    (models.OrderItem.size == "XXL", models.Product.XXL_price),
                    else_=0
                )
            ).label("total_price"),
            models.Order.time.label("order_time")
        )
        .join(models.User, models.Order.user_id == models.User.id)
        .join(models.OrderItem, models.Order.id == models.OrderItem.order_id)
        .join(models.Product, models.OrderItem.product_id == models.Product.id)
        .filter(models.Order.user_id == user_id)
        .group_by(models.Order.id, models.User.username)
        .all()
    )

    orders = []
    for r in results:
        order_items = db.query(
            models.OrderItem.quantity,
            models.OrderItem.size,
            models.OrderItem.product_id,
            models.Product.name.label("product_name"),
            models.Product.XS_price,
            models.Product.S_price,
            models.Product.M_price,
            models.Product.L_price,
            models.Product.XL_price,
            models.Product.XXL_price,
        ).join(models.Product, models.OrderItem.product_id == models.Product.id) \
         .filter(models.OrderItem.order_id == r.order_id).all()

        products = [
            schemas.OrderProduct(
                product_name=item.product_name,
                quantity=item.quantity,
                size=item.size,
                product_id=item.product_id,
                color=getattr(item, "color", None) or None,
                price=(
                    item.XS_price if item.size == "XS" else
                    item.S_price if item.size == "S" else
                    item.M_price if item.size == "M" else
                    item.L_price if item.size == "L" else
                    item.XL_price if item.size == "XL" else
                    item.XXL_price
                ) * item.quantity
            ) for item in order_items
        ]

        orders.append(
            schemas.OrderResponse(
                order_id=r.order_id,
                user_id=r.user_id,
                username=r.username,
                status=r.status,
                total_products=r.total_products,
                total_price=int(r.total_price or 0),
                products=products,
                order_time=r.order_time
            )
        )
    return orders


def get_order(db: Session, order_id: int):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        return None

    items = (
        db.query(models.OrderItem, models.Product)
        .join(models.Product, models.OrderItem.product_id == models.Product.id)
        .filter(models.OrderItem.order_id == order_id)
        .all()
    )

    total_price = sum(
        item.OrderItem.quantity * getattr(item.Product, f"{item.OrderItem.size}_price")
        for item in items
    )

    products = [
        schemas.OrderProduct(
            product_name=item.Product.name,
            quantity=item.OrderItem.quantity,
            size=item.OrderItem.size,
            product_id=item.OrderItem.product_id,
            color=item.OrderItem.color,
            price=item.OrderItem.quantity * getattr(item.Product, f"{item.OrderItem.size}_price")
        ) for item in items
    ]

    return schemas.OrderResponse(
        order_id=order.id,
        user_id=order.user_id,
        username=order.user.username,
        status=order.status,
        total_products=len(products),
        total_price=int(total_price),
        products=products,
        order_time=order.time
    )


def update_order_status(db: Session, order_id: int, status: str):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        return None
    order.status = status
    db.commit()
    db.refresh(order)
    return order


def create_order_from_cart(db: Session, order: schemas.OrderCreate):
    user = db.query(models.User).filter(models.User.id == order.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    cart_items = db.query(models.Cart).filter(models.Cart.user_id == order.user_id).all()
    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    try:
        order_time = datetime.fromisoformat(order.order_time.replace('Z', '+00:00')).date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid order_time format")

    db_order = models.Order(
        user_id=order.user_id,
        status="pending",
        time=order_time
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    for item in cart_items:
        db_item = models.OrderItem(
            order_id=db_order.id,
            product_id=item.product_id,
            size=item.size,
            quantity=item.quantity,
            color=item.color
        )
        db.add(db_item)

    db.query(models.Cart).filter(models.Cart.user_id == order.user_id).delete()
    db.commit()

    return get_user_orders(db, order.user_id)
