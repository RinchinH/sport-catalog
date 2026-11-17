
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.product import ProductCreate, ProductResponse
from app.services.products import (
    get_all_products,
    create_product
)


router = APIRouter(
    prefix="/api/products",
    tags=["Каталог товаров"]
)


# Получение всех товаров
@router.get("", response_model=list[ProductResponse])
async def list_products(
    db: AsyncSession = Depends(get_db)
):
    return await get_all_products(db)


# Создание нового товара
@router.post(
    "",
    response_model=ProductResponse,
    status_code=201
)
async def add_product(
    data: ProductCreate,
    db: AsyncSession = Depends(get_db)
):
    return await create_product(
        db=db,
        name=data.name,
        price=data.price,
        stock=data.stock
    )
