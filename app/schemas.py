from datetime import datetime
from typing import Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field
)


# =========================
# AUTH
# =========================

class RegisterRequest(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=100
    )

    email: EmailStr

    password: str = Field(
        min_length=6,
        max_length=100
    )


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    is_admin: bool

    model_config = ConfigDict(
        from_attributes=True
    )


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


# =========================
# PRODUCT
# =========================

class ProductCreate(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=200
    )

    description: str = Field(
        min_length=1
    )

    price: float = Field(
        gt=0
    )

    image_url: Optional[str] = None


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=200
    )

    description: Optional[str] = None

    price: Optional[float] = Field(
        default=None,
        gt=0
    )

    image_url: Optional[str] = None


class ProductResponse(BaseModel):
    id: int
    name: str
    description: str
    price: float
    image_url: Optional[str]
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class ProductListResponse(BaseModel):
    items: list[ProductResponse]
    page: int
    limit: int
    total: int
    total_pages: int


# =========================
# CART
# =========================

class CartItemCreate(BaseModel):
    product_id: int

    quantity: int = Field(
        gt=0
    )


class CartItemUpdate(BaseModel):
    quantity: int = Field(
        gt=0
    )


class CartItemResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    price: float
    quantity: int
    subtotal: float


class CartResponse(BaseModel):
    items: list[CartItemResponse]
    total_amount: float


# =========================
# ORDER
# =========================

class OrderItemResponse(BaseModel):
    product_id: int
    product_name: str
    quantity: int
    price: float
    subtotal: float


class OrderResponse(BaseModel):
    id: int
    total_amount: float
    status: str
    payment_status: Optional[str]
    created_at: datetime
    items: list[OrderItemResponse]


class OrderListResponse(BaseModel):
    items: list[OrderResponse]
    page: int
    limit: int
    total: int
    total_pages: int


# =========================
# PAYMENT
# =========================

class CheckoutResponse(BaseModel):
    checkout_url: str
    order_id: int


# =========================
# ADMIN
# =========================

class AdminStatsResponse(BaseModel):
    total_products: int
    total_orders: int
    paid_orders: int
    total_revenue: float