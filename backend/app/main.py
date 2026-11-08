import os
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone

import jwt
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash

from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import String, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import (
    create_async_engine, async_sessionmaker, AsyncSession
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


DATABASE_URL = os.environ["DATABASE_URL"]
JWT_SECRET = os.environ["JWT_SECRET"]

engine = create_async_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

password_hasher = PasswordHash.recommended()
bearer_scheme = HTTPBearer(auto_error=False)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(
        String(50), unique=True, index=True, nullable=False
    )
    password_hash: Mapped[str] = mapped_column(
        String(512), nullable=False
    )
    role: Mapped[str] = mapped_column(
        String(20), default="buyer", nullable=False
    )


class RegisterRequest(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_]+$"
    )
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    role: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


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


async def get_db():
    async with SessionLocal() as session:
        yield session


async def current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(
        bearer_scheme
    ),
    db: AsyncSession = Depends(get_db),
):
    if credentials is None:
        raise HTTPException(status_code=401, detail="Требуется вход")

    try:
        data = jwt.decode(
            credentials.credentials,
            JWT_SECRET,
            algorithms=["HS256"]
        )
        user_id = int(data["sub"])
    except (InvalidTokenError, KeyError, ValueError):
        raise HTTPException(
            status_code=401, detail="Неверный или просроченный токен"
        )

    user = await db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="Пользователь не найден")
    return user


@app.get("/api/health")
async def health(db: AsyncSession = Depends(get_db)):
    await db.scalar(select(1))
    return {"status": "ok"}


@app.post(
    "/api/auth/register",
    response_model=UserResponse,
    status_code=201
)
async def register(
    data: RegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    user = User(
        username=data.username,
        password_hash=password_hasher.hash(data.password),
        role="buyer"
    )
    db.add(user)

    try:
        await db.commit()
        await db.refresh(user)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Такой логин уже занят"
        )

    return user


@app.post("/api/auth/login", response_model=TokenResponse)
async def login(
    data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    user = await db.scalar(
        select(User).where(User.username == data.username)
    )

    if user is None or not password_hasher.verify(
        data.password, user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Неверный логин или пароль"
        )

    token = jwt.encode(
        {
            "sub": str(user.id),
            "exp": datetime.now(timezone.utc) + timedelta(hours=1)
        },
        JWT_SECRET,
        algorithm="HS256"
    )

    return TokenResponse(access_token=token)


@app.get("/api/auth/me", response_model=UserResponse)
async def get_profile(user: User = Depends(current_user)):
    return user
