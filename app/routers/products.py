import math

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status
)

from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import get_admin_user
from ..models import Product, User

from ..schemas import (
    ProductCreate,
    ProductListResponse,
    ProductResponse,
    ProductUpdate
)


router = APIRouter(
    prefix="/products",
    tags=["Products"]
)


@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED
)
def create_product(
    data: ProductCreate,
    db: Session = Depends(get_db),
    #admin: User = Depends(get_admin_user)
):
    product = Product(
        name=data.name,
        description=data.description,
        price=data.price,
        image_url=data.image_url
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    return product


@router.get(
    "",
    response_model=ProductListResponse
)
def get_products(
    page: int = Query(
        1,
        ge=1
    ),

    limit: int = Query(
        10,
        ge=1,
        le=100
    ),

    search: str = "",

    db: Session = Depends(get_db)
):
    query = db.query(Product)

    if search:
        query = query.filter(
            Product.name.ilike(
                f"%{search}%"
            )
        )

    total = query.count()

    products = query.order_by(
        Product.id.desc()
    ).offset(
        (page - 1) * limit
    ).limit(limit).all()

    total_pages = (
        math.ceil(total / limit)
        if total > 0
        else 0
    )

    return {
        "items": products,
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": total_pages
    }


@router.get(
    "/{product_id}",
    #response_model=ProductResponse
)
def get_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    product = db.query(
        Product
    ).filter(
        Product.id == product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    return product


@router.put(
    "/{product_id}",
    response_model=ProductResponse
)
def update_product(
    product_id: int,
    data: ProductUpdate,
    db: Session = Depends(get_db),
    #admin: User = Depends(get_admin_user)
):
    product = db.query(
        Product
    ).filter(
        Product.id == product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    update_data = data.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():
        setattr(
            product,
            key,
            value
        )

    db.commit()
    db.refresh(product)

    return product


@router.delete(
    "/{product_id}"
)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    #admin: User = Depends(get_admin_user)
):
    product = db.query(
        Product
    ).filter(
        Product.id == product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    db.delete(product)
    db.commit()

    return {
        "message": "Product deleted successfully"
    }