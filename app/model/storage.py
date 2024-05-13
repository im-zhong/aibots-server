# 2024/5/13
# zhangzhong

from pydantic import BaseModel, Field
from enum import Enum


class Role(str, Enum):
    USER = "user"
    ADMIN = "admin"
