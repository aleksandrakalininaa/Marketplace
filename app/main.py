from fastapi import FastAPI

from app.database import engine, Base
from app.routers import auth, products, orders, reviews

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Marketplace API", version="0.1.0")

app.include_router(auth.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(reviews.router)


@app.get("/")
def root():
    return {"message": "Welcome to Marketplace API"}