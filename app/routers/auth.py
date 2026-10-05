from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)

from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.orm import Session

from ..auth import (
    create_access_token,
    hash_password,
    verify_password
)

from ..database import get_db

from ..dependencies import get_current_user

from ..models import (
    Cart,
    User
)

from ..schemas import (
    RegisterRequest,
    TokenResponse,
    UserResponse
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# ==========================================
# REGISTER
# ==========================================

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register(
    data: RegisterRequest,
    db: Session = Depends(get_db)
):
    # Check if email already exists
    existing_user = db.query(
        User
    ).filter(
        User.email == data.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    # Create user
    user = User(
        name=data.name,
        email=data.email,
        password_hash=hash_password(
            data.password
        ),
        is_admin=False
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    # Create cart for the user
    cart = Cart(
        user_id=user.id
    )

    db.add(cart)
    db.commit()

    return user


# ==========================================
# LOGIN
# ==========================================

@router.post(
    "/login",
    response_model=TokenResponse
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # Find user by email
    user = db.query(
        User
    ).filter(
        User.email == form_data.username
    ).first()

    # Check email and password
    if not user or not verify_password(
        form_data.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    # Create JWT token
    token = create_access_token(
        user.id
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }


# ==========================================
# CURRENT USER / PROFILE
# ==========================================

@router.get(
    "/me",
    response_model=UserResponse
)
def profile(
    current_user: User = Depends(
        get_current_user
    )
):
    return current_user