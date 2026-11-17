
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order


async def get_user_orders(
    db: AsyncSession,
    user_id: int
) -> list[Order]:

    result = await db.scalars(
        select(Order)
        .options(selectinload(Order.items))
        .where(Order.user_id == user_id)
        .order_by(Order.created_at.desc())
    )

    return list(result.all())
