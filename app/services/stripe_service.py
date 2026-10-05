import stripe

from ..database import settings


stripe.api_key = settings.STRIPE_SECRET_KEY


def create_checkout_session(
    order_id: int,
    line_items: list
):
    return stripe.checkout.Session.create(
        payment_method_types=["card"],

        line_items=line_items,

        mode="payment",

        success_url=(
            f"{settings.FRONTEND_URL}"
            f"/orders?payment=success"
        ),

        cancel_url=(
            f"{settings.FRONTEND_URL}"
            f"/cart?payment=cancelled"
        ),

        metadata={
            "order_id": str(order_id)
        }
    )