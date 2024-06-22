# 2024/5/15
# zhangzhong

from typing import AsyncGenerator
from uuid import UUID

from fastapi import Depends
from fastapi_users import FastAPIUsers
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from app.storage.database import Database, async_session_maker
from app.storage.schema import UserSchema
from app.user.auth_backend import auth_backend
from app.user.user_manager import UserManager


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, UserSchema)


async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)


async def get_db(session: AsyncSession = Depends(get_async_session)):
    yield Database(session)


fastapi_users = FastAPIUsers[UserSchema, UUID](
    get_user_manager=get_user_manager,
    auth_backends=[auth_backend],
)


async def get_current_user(
    user: UserSchema = Depends(fastapi_users.current_user(active=True, verified=True)),
):
    yield user


# https://github.com/fastapi-users/fastapi-users/issues/295
async def get_user_from_token(
    token: str, user_manager=Depends(dependency=get_user_manager)
):
    print("try to auth user")
    user: UserSchema | None = await auth_backend.get_strategy().read_token(  # type: ignore
        token, user_manager
    )
    if not user or not user.is_active or not user.is_verified:
        raise ValueError("Invalid user")
    yield user
