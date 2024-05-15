from typing import Optional
from uuid import UUID

from fastapi import Request
from fastapi_users import BaseUserManager, UUIDIDMixin

from app.storage.schema import UserSchema

SECRET = "SECRET"


class UserManager(UUIDIDMixin, BaseUserManager[UserSchema, UUID]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(
        self, user: UserSchema, request: Optional[Request] = None
    ):
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(
        self, user: UserSchema, token: str, request: Optional[Request] = None
    ):
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
        self, user: UserSchema, token: str, request: Optional[Request] = None
    ):
        print(f"Verification requested for user {user.id}. Verification token: {token}")
