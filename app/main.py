from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import (
    Base,
    engine
)

from .routers import (
    auth,
    products,
    cart,
    orders,
    payments,
    admin,
    reports
)


Base.metadata.create_all(
    bind=engine
)


app = FastAPI(
    title="Digital Product Store API",
    description=(
        "Backend API for a digital "
        "product store"
    ),
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


app.include_router(
    auth.router
)

app.include_router(
    products.router
)

app.include_router(
    cart.router
)

app.include_router(
    orders.router
)

app.include_router(
    payments.router
)

app.include_router(
    admin.router
)

app.include_router(
    reports.router
)


@app.get("/")
def root():
    return {
        "message": (
            "Digital Product Store API "
            "is running"
        )
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }