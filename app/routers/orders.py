import math

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query
)

from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import get_current_user

from ..models import Order, User

from ..schemas import (
    OrderListResponse,
    OrderResponse
)


router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)


def build_order_response(
    order: Order
):
    items = []

    for item in order.items:

        items.append({
            "product_id": item.product_id,
            "product_name": item.product.name,
            "quantity": item.quantity,
            "price": item.price,
            "subtotal": round(
                item.price * item.quantity,
                2
            )
        })

    payment_status = None

    if order.payment:
        payment_status = order.payment.status

    return {
        "id": order.id,
        "total_amount": order.total_amount,
        "status": order.status,
        "payment_status": payment_status,
        "created_at": order.created_at,
        "items": items
    }


@router.get(
    "",
    response_model=OrderListResponse
)
def get_orders(
    page: int = Query(
        1,
        ge=1
    ),

    limit: int = Query(
        5,
        ge=1,
        le=100
    ),

    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(get_db)
):
    query = db.query(
        Order
    ).filter(
        Order.user_id == current_user.id
    )

    total = query.count()

    orders = query.order_by(
        Order.id.desc()
    ).offset(
        (page - 1) * limit
    ).limit(limit).all()

    total_pages = (
        math.ceil(total / limit)
        if total
        else 0
    )

    return {
        "items": [
            build_order_response(order)
            for order in orders
        ],
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": total_pages
    }


@router.get(
    "/{order_id}",
    response_model=OrderResponse
)
def get_order(
    order_id: int,

    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(get_db)
):
    order = db.query(
        Order
    ).filter(
        Order.id == order_id,
        Order.user_id == current_user.id
    ).first()

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    return build_order_response(
        order
    )