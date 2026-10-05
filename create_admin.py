from app.auth import hash_password
from app.database import SessionLocal
from app.models import User, Cart


def create_admin():
    db = SessionLocal()

    try:
        email = input(
            "Enter admin email: "
        ).strip()

        password = input(
            "Enter admin password: "
        ).strip()

        name = input(
            "Enter admin name: "
        ).strip()

        existing = db.query(
            User
        ).filter(
            User.email == email
        ).first()

        if existing:
            print(
                "User with this email already exists."
            )

            existing.is_admin = True

            db.commit()

            print(
                "Existing user promoted to admin."
            )

            return

        user = User(
            name=name,
            email=email,
            password_hash=hash_password(
                password
            ),
            is_admin=True
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        cart = Cart(
            user_id=user.id
        )

        db.add(cart)
        db.commit()

        print(
            "Admin created successfully."
        )

    finally:
        db.close()


if __name__ == "__main__":
    create_admin()