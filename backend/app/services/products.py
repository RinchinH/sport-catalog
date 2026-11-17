
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product


# Получение всех товаров
async def get_all_products(db: AsyncSession) -> list[Product]:
    result = await db.scalars(
        select(Product).order_by(Product.id)
    )

    return list(result.all())


# Создание нового товара
async def create_product(
    db: AsyncSession,
    name: str,
    price: Decimal,
    stock: int
) -> Product:

    product = Product(
        name=name,
        price=price,
        stock=stock
    )

    db.add(product)

    await db.commit()
    await db.refresh(product)

    return product
