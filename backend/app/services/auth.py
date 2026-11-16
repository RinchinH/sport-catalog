
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token
)
from app.models.user import User


class UsernameAlreadyExistsError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


async def register_user(
    db: AsyncSession,
    username: str,
    password: str
) -> User:
    user = User(
        username=username,
        password_hash=hash_password(password),
        role="buyer"
    )

    db.add(user)

    try:
        await db.commit()
        await db.refresh(user)
    except IntegrityError as exc:
        await db.rollback()
        raise UsernameAlreadyExistsError from exc

    return user


async def login_user(
    db: AsyncSession,
    username: str,
    password: str
) -> str:
    user = await db.scalar(
        select(User).where(User.username == username)
    )

    if user is None or not verify_password(
        password, user.password_hash
    ):
        raise InvalidCredentialsError

    return create_access_token(user.id)
