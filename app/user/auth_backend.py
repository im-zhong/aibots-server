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
from app.model import UserUpdate
from app.model.user import UserCreate, UserOut
from app.storage.schema import UserSchema

cookie_transport = CookieTransport(cookie_max_age=3600)
myredis = redis.asyncio.from_url(url=conf.redis_url, decode_responses=True)


def get_redis_strategy() -> RedisStrategy:
    return RedisStrategy(redis=myredis, lifetime_seconds=3600)


# redis only for user cookie
# cause user login would get its cookie from database, redis can speed that up
# but for token, fastapiusers do not store it in the database, otherwise, it use JWT
# but JWT could not be cancelled, so how do fastapiusers ackowledge that token is used for verifycation or reset-password?
# in verifycatin, it's easy, because we could set the user state in database, if user is verified, that token is cancelled.
# but how about reset password?
# 我想起来了，在保存密码的时候，都需要加盐，而且每次重置密码都会重置盐
# 也就是说，salt对于每个密码都是不同的，也就是说，即使用户的密码明文相同，哈希之后的密码也不同
# 在重置密码的时候，我们使用哈希算法，将数据库中的(哈希之后的密码+盐)再哈希一次，作为jwt的token
# 这样，首先jwt防止篡改，我们就可以使用这个jwt作为验证
# 并且，一旦用户修改了密码，即使密码和之前一样，数据库中的（哈希之后的密码+盐）也会不一样，所以这个生成的jwt只能使用一次
auth_backend = AuthenticationBackend(
    name="cookie_redis",
    transport=cookie_transport,  # On logout, This method will remove the authentication cookie
    get_strategy=get_redis_strategy,  # On logout, this strategy will delete the token from the Redis store.
)

# fastapi_users = FastAPIUsers[UserSchema, UUID](
#     get_user_manager=get_user_manager,
#     auth_backends=[auth_backend],
# )
