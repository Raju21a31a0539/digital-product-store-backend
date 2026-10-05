from fastapi import (
    APIRouter,
    Depends
)

from sqlalchemy import func
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import get_admin_user

from ..models import (
    Order,
    OrderItem,
    Product,
    User
)


router = APIRouter(
    prefix="/reports",
    tags=["Reports"]
)


# 1. Total revenue

@router.get("/total-revenue")
def total_revenue(
    admin: User = Depends(
        get_admin_user
    ),

    db: Session = Depends(get_db)
):
    revenue = db.query(
        func.sum(Order.total_amount)
    ).filter(
        Order.status == "PAID"
    ).scalar()

    return {
        "total_revenue": round(
            revenue or 0,
            2
        )
    }


# 2. Most purchased products

@router.get("/most-purchased-products")
def most_purchased_products(
    admin: User = Depends(
        get_admin_user
    ),

    db: Session = Depends(get_db)
):
    results = db.query(
        Product.id,
        Product.name,
        func.sum(
            OrderItem.quantity
        ).label("total_quantity")
    ).join(
        OrderItem,
        Product.id == OrderItem.product_id
    ).join(
        Order,
        Order.id == OrderItem.order_id
    ).filter(
        Order.status == "PAID"
    ).group_by(
        Product.id,
        Product.name
    ).order_by(
        func.sum(
            OrderItem.quantity
        ).desc()
    ).all()

    return [
        {
            "product_id": row.id,
            "product_name": row.name,
            "total_quantity": row.total_quantity
        }

        for row in results
    ]


# 3. Products never purchased

@router.get("/never-purchased-products")
def never_purchased_products(
    admin: User = Depends(
        get_admin_user
    ),

    db: Session = Depends(get_db)
):
    products = db.query(
        Product
    ).outerjoin(
        OrderItem,
        Product.id == OrderItem.product_id
    ).filter(
        OrderItem.id.is_(None)
    ).all()

    return [
        {
            "id": product.id,
            "name": product.name,
            "price": product.price
        }

        for product in products
    ]


# 4. Number of orders per user

@router.get("/orders-per-user")
def orders_per_user(
    admin: User = Depends(
        get_admin_user
    ),

    db: Session = Depends(get_db)
):
    results = db.query(
        User.id,
        User.email,
        func.count(
            Order.id
        ).label("order_count")
    ).outerjoin(
        Order,
        User.id == Order.user_id
    ).group_by(
        User.id,
        User.email
    ).all()

    return [
        {
            "user_id": row.id,
            "email": row.email,
            "order_count": row.order_count
        }

        for row in results
    ]