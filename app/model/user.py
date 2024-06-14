# 2024/5/15
# zhangzhong

from datetime import datetime
from uuid import UUID

from fastapi_users.schemas import BaseUser, BaseUserCreate, BaseUserUpdate


class UserOut(BaseUser[UUID]):
    name: str
    created_at: datetime


class UserCreate(BaseUserCreate):
    name: str


class UserUpdate(BaseUserUpdate):
    name: str
