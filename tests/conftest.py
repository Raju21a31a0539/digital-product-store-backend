import os

os.environ["DATABASE_URL"] = (
    "sqlite:///./test_store.db"
)

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app


TEST_DATABASE_URL = (
    "sqlite:///./test_store.db"
)


engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={
        "check_same_thread": False
    }
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def override_get_db():
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[
    get_db
] = override_get_db


Base.metadata.create_all(
    bind=engine
)


client = TestClient(app)


def get_token(
    email,
    password
):
    response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password
        }
    )

    return response.json()[
        "access_token"
    ]