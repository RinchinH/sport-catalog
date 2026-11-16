
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db


router = APIRouter(tags=["Проверка сервера"])


@router.get("/api/health")
async def health(db: AsyncSession = Depends(get_db)):
    await db.scalar(select(1))
    return {"status": "ok"}
