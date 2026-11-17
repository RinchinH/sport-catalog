
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db.base import Base
from app.db.database import engine
from app.models.user import User
from app.models.product import Product
from app.models.order import Order, OrderItem
from app.api.routes.auth import router as auth_router
from app.api.routes.health import router as health_router
from app.api.routes.products import router as products_router
from app.api.routes.orders import router as orders_router
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    yield

    await engine.dispose()


app = FastAPI(
    title="СпортКаталог API",
    lifespan=lifespan,
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)


app.include_router(auth_router)
app.include_router(health_router)
app.include_router(products_router)
app.include_router(orders_router)