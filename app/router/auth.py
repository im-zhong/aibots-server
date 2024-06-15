# 2024/5/15
# zhangzhong

from typing import Optional
from uuid import UUID

import redis.asyncio
from fastapi import APIRouter, Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin
from fastapi_users.authentication import (
    AuthenticationBackend,
    CookieTransport,
    RedisStrategy,
)
from fastapi_users.db import SQLAlchemyUserDatabase

from app.common import conf
from app.model.user import UserCreate, UserOut
from app.router.dependency import get_user_manager
from app.storage.schema import UserSchema

cookie_transport = CookieTransport(cookie_max_age=3600)
myredis = redis.asyncio.from_url(url=conf.redis_url, decode_responses=True)


def get_redis_strategy() -> RedisStrategy:
    return RedisStrategy(myredis, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="cookie_redis",
    transport=cookie_transport,  # On logout, This method will remove the authentication cookie
    get_strategy=get_redis_strategy,  # On logout, this strategy will delete the token from the Redis store.
)

fastapi_users = FastAPIUsers[UserSchema, UUID](
    get_user_manager=get_user_manager,
    auth_backends=[auth_backend],
)
# current_active_user = fastapi_users.current_user(active=True)
auth = APIRouter(prefix="/api/auth", tags=["auth"])

auth.include_router(
    fastapi_users.get_auth_router(
        backend=auth_backend,
        requires_verification=True,
    )
)
auth.include_router(fastapi_users.get_register_router(UserOut, UserCreate))
auth.include_router(fastapi_users.get_reset_password_router())
auth.include_router(fastapi_users.get_verify_router(UserOut))
