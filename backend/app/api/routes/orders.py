
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, current_user
from app.models.user import User
from app.schemas.order import OrderResponse
from app.services.orders import get_user_orders


router = APIRouter(
    prefix="/api/orders",
    tags=["Заказы"]
)


@router.get(
    "",
    response_model=list[OrderResponse]
)
async def list_my_orders(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_user)
):
    return await get_user_orders(
        db,
        user.id
    )
