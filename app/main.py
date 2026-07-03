import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine, Base
from app.models import User, VkAccount, RefreshToken, PasswordResetToken, Product, Order, OrderItem, Review, Category, CatalogProduct  # noqa: F401
from app.routers import auth, products, orders, reviews, catalog

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Создание таблиц при старте (в прод-режиме использовать Alembic миграции)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created")
    yield
    await engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(catalog.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(reviews.router)


@app.get("/")
async def root():
    return {"message": "Welcome to Marketplace API"}