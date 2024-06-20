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
