from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import get_current_user

from ..models import (
    Cart,
    CartItem,
    Product,
    User
)

from ..schemas import (
    CartItemCreate,
    CartItemUpdate,
    CartResponse
)


router = APIRouter(
    prefix="/cart",
    tags=["Cart"]
)


def get_or_create_cart(
    user: User,
    db: Session
):
    cart = db.query(
        Cart
    ).filter(
        Cart.user_id == user.id
    ).first()

    if not cart:
        cart = Cart(
            user_id=user.id
        )

        db.add(cart)
        db.commit()
        db.refresh(cart)

    return cart


def build_cart_response(
    cart: Cart
):
    items = []
    total = 0

    for item in cart.items:
        subtotal = (
            item.product.price
            * item.quantity
        )

        items.append({
            "id": item.id,
            "product_id": item.product_id,
            "product_name": item.product.name,
            "price": item.product.price,
            "quantity": item.quantity,
            "subtotal": round(
                subtotal,
                2
            )
        })

        total += subtotal

    return {
        "items": items,
        "total_amount": round(
            total,
            2
        )
    }


@router.get(
    "",
    response_model=CartResponse
)
def get_cart(
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db)
):
    cart = get_or_create_cart(
        current_user,
        db
    )

    return build_cart_response(
        cart
    )


@router.post(
    "/items",
    response_model=CartResponse
)
def add_to_cart(
    data: CartItemCreate,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db)
):
    product = db.query(
        Product
    ).filter(
        Product.id == data.product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    cart = get_or_create_cart(
        current_user,
        db
    )

    item = db.query(
        CartItem
    ).filter(
        CartItem.cart_id == cart.id,
        CartItem.product_id == data.product_id
    ).first()

    if item:
        item.quantity += data.quantity
    else:
        item = CartItem(
            cart_id=cart.id,
            product_id=data.product_id,
            quantity=data.quantity
        )

        db.add(item)

    db.commit()
    db.refresh(cart)

    return build_cart_response(
        cart
    )


@router.put(
    "/items/{item_id}",
    response_model=CartResponse
)
def update_cart_item(
    item_id: int,
    data: CartItemUpdate,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db)
):
    cart = get_or_create_cart(
        current_user,
        db
    )

    item = db.query(
        CartItem
    ).filter(
        CartItem.id == item_id,
        CartItem.cart_id == cart.id
    ).first()

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Cart item not found"
        )

    item.quantity = data.quantity

    db.commit()
    db.refresh(cart)

    return build_cart_response(
        cart
    )


@router.delete(
    "/items/{item_id}",
    response_model=CartResponse
)
def remove_cart_item(
    item_id: int,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db)
):
    cart = get_or_create_cart(
        current_user,
        db
    )

    item = db.query(
        CartItem
    ).filter(
        CartItem.id == item_id,
        CartItem.cart_id == cart.id
    ).first()

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Cart item not found"
        )

    db.delete(item)
    db.commit()
    db.refresh(cart)

    return build_cart_response(
        cart
    )


@router.delete("")
def clear_cart(
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db)
):
    cart = get_or_create_cart(
        current_user,
        db
    )

    for item in list(cart.items):
        db.delete(item)

    db.commit()

    return {
        "message": "Cart cleared successfully"
    }