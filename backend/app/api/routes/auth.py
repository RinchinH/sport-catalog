
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import current_user, get_db
from app.models.user import User
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    UserResponse,
    TokenResponse
)
from app.services.auth import (
    register_user,
    login_user,
    UsernameAlreadyExistsError,
    InvalidCredentialsError
)


router = APIRouter(
    prefix="/api/auth",
    tags=["Авторизация"]
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=201
)
async def register(
    data: RegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        user = await register_user(
            db,
            data.username,
            data.password
        )
    except UsernameAlreadyExistsError:
        raise HTTPException(
            status_code=409,
            detail="Такой логин уже занят"
        )

    return user


@router.post("/login", response_model=TokenResponse)
async def login(
    data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        token = await login_user(
            db,
            data.username,
            data.password
        )
    except InvalidCredentialsError:
        raise HTTPException(
            status_code=401,
            detail="Неверный логин или пароль"
        )

    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserResponse)
async def get_profile(
    user: User = Depends(current_user)
):
    return user
