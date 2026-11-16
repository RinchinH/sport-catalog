
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from jwt.exceptions import InvalidTokenError

from app.core.security import decode_access_token
from app.db.database import SessionLocal
from app.models.user import User


bearer_scheme = HTTPBearer(auto_error=False)


async def get_db():
    async with SessionLocal() as session:
        yield session


async def current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(
        bearer_scheme
    ),
    db: AsyncSession = Depends(get_db)
) -> User:
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Требуется вход"
        )

    try:
        payload = decode_access_token(credentials.credentials)
        user_id = int(payload["sub"])

    except (InvalidTokenError, KeyError, TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=401,
            detail="Неверный или просроченный токен"
        ) from exc

    user = await db.get(User, user_id)

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Пользователь не найден"
        )

    return user
