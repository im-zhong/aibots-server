# 2024/5/15
# zhangzhong


from fastapi import APIRouter

from app.model.user import UserCreate, UserOut
from app.router.dependency import fastapi_users
from app.user.auth_backend import auth_backend

auth = APIRouter(prefix="/api/auth", tags=["auth"])

auth.include_router(
    fastapi_users.get_auth_router(
        backend=auth_backend,
        requires_verification=True,
    )
)
auth.include_router(
    fastapi_users.get_register_router(
        UserOut,
        UserCreate,
    )
)
auth.include_router(fastapi_users.get_reset_password_router())
auth.include_router(fastapi_users.get_verify_router(UserOut))
