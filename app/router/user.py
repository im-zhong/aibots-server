# 2024/5/15
# zhangzhong


from fastapi import APIRouter

from app.model import UserOut, UserUpdate
from app.router.dependency import fastapi_users

user = APIRouter(prefix="/api/user", tags=["user"])

user.include_router(
    router=fastapi_users.get_users_router(
        user_schema=UserOut,
        user_update_schema=UserUpdate,
        requires_verification=True,
    ),
)
