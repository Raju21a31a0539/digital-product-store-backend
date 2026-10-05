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
    Product,
    User
)

from ..schemas import (
    AdminStatsResponse
)


router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)


@router.get(
    "/stats",
    response_model=AdminStatsResponse
)
def get_stats(
    admin: User = Depends(
        get_admin_user
    ),

    db: Session = Depends(get_db)
):
    total_products = db.query(
        Product
    ).count()

    total_orders = db.query(
        Order
    ).count()

    paid_orders = db.query(
        Order
    ).filter(
        Order.status == "PAID"
    ).count()

    revenue = db.query(
        func.sum(
            Order.total_amount
        )
    ).filter(
        Order.status == "PAID"
    ).scalar()

    return {
        "total_products": total_products,
        "total_orders": total_orders,
        "paid_orders": paid_orders,
        "total_revenue": round(
            revenue or 0,
            2
        )
    }


@router.get(
    "/orders"
)
def get_all_orders(
    admin: User = Depends(
        get_admin_user
    ),

    db: Session = Depends(get_db)
):
    orders = db.query(
        Order
    ).order_by(
        Order.id.desc()
    ).all()

    return [
        {
            "id": order.id,
            "user_id": order.user_id,
            "user_email": order.user.email,
            "total_amount": order.total_amount,
            "status": order.status,
            "payment_status": (
                order.payment.status
                if order.payment
                else None
            ),
            "created_at": order.created_at
        }

        for order in orders
    ]