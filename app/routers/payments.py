import stripe

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request
)

from sqlalchemy.orm import Session

from ..database import (
    get_db,
    settings
)

from ..dependencies import (
    get_current_user
)

from ..models import (
    Cart,
    Order,
    OrderItem,
    Payment,
    User
)

from ..schemas import (
    CheckoutResponse
)

from ..services.stripe_service import (
    create_checkout_session
)


router = APIRouter(
    prefix="/payments",
    tags=["Payments"]
)


@router.post(
    "/create-checkout-session",
    response_model=CheckoutResponse
)
def create_checkout(
    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(get_db)
):
    cart = db.query(
        Cart
    ).filter(
        Cart.user_id == current_user.id
    ).first()

    if not cart or not cart.items:
        raise HTTPException(
            status_code=400,
            detail="Cart is empty"
        )

    total = 0

    line_items = []

    for item in cart.items:

        if item.quantity <= 0:
            raise HTTPException(
                status_code=400,
                detail="Invalid product quantity"
            )

        total += (
            item.product.price
            * item.quantity
        )

        line_items.append({
            "price_data": {
                "currency": "usd",

                "product_data": {
                    "name": item.product.name,
                    "description": item.product.description
                },

                "unit_amount": int(
                    round(
                        item.product.price * 100
                    )
                )
            },

            "quantity": item.quantity
        })

    total = round(
        total,
        2
    )

    order = Order(
        user_id=current_user.id,
        total_amount=total,
        status="PENDING"
    )

    db.add(order)
    db.commit()
    db.refresh(order)

    for item in cart.items:

        order_item = OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=item.product.price
        )

        db.add(order_item)

    db.commit()

    try:

        session = create_checkout_session(
            order.id,
            line_items
        )

        payment = Payment(
            order_id=order.id,
            stripe_session_id=session.id,
            amount=total,
            status="PENDING"
        )

        db.add(payment)
        db.commit()

        return {
            "checkout_url": session.url,
            "order_id": order.id
        }

    except stripe.StripeError as exc:

        order.status = "FAILED"

        db.commit()

        raise HTTPException(
            status_code=400,
            detail=f"Stripe error: {str(exc)}"
        )


@router.post(
    "/webhook"
)
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    payload = await request.body()

    signature = request.headers.get(
        "stripe-signature"
    )

    if not signature:
        raise HTTPException(
            status_code=400,
            detail="Missing Stripe signature"
        )

    try:

        event = stripe.Webhook.construct_event(
            payload,
            signature,
            settings.STRIPE_WEBHOOK_SECRET
        )

    except ValueError:

        raise HTTPException(
            status_code=400,
            detail="Invalid webhook payload"
        )

    except stripe.SignatureVerificationError:

        raise HTTPException(
            status_code=400,
            detail="Invalid webhook signature"
        )

    event_type = event["type"]

    if event_type == "checkout.session.completed":

        session = event["data"]["object"]

        metadata = session.get(
            "metadata",
            {}
        )

        order_id = metadata.get(
            "order_id"
        )

        if order_id:

            order = db.query(
                Order
            ).filter(
                Order.id == int(order_id)
            ).first()

            if order:

                order.status = "PAID"

                payment = db.query(
                    Payment
                ).filter(
                    Payment.order_id == order.id
                ).first()

                if payment:
                    payment.status = "PAID"

                cart = db.query(
                    Cart
                ).filter(
                    Cart.user_id == order.user_id
                ).first()

                if cart:

                    for item in list(cart.items):
                        db.delete(item)

                db.commit()

    elif event_type == "checkout.session.expired":

        session = event["data"]["object"]

        metadata = session.get(
            "metadata",
            {}
        )

        order_id = metadata.get(
            "order_id"
        )

        if order_id:

            order = db.query(
                Order
            ).filter(
                Order.id == int(order_id)
            ).first()

            if order:

                order.status = "CANCELLED"

                payment = db.query(
                    Payment
                ).filter(
                    Payment.order_id == order.id
                ).first()

                if payment:
                    payment.status = "CANCELLED"

                db.commit()

    return {
        "received": True
    }