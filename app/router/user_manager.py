import smtplib
from email.mime.text import MIMEText
from typing import Optional
from uuid import UUID

from fastapi import Request
from fastapi_users import BaseUserManager, UUIDIDMixin

from app.common import conf
from app.storage.schema import UserSchema

SECRET = "SECRET"


def send_email(subject: str, message: str, to_email: str):
    from_email = conf.smtp_email
    password = conf.smtp_password

    msg = MIMEText(message)
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email

    server = smtplib.SMTP_SSL(host=conf.smtp_server, port=conf.smtp_port)
    # server.starttls()
    server.login(from_email, password)
    server.send_message(msg)
    server.quit()


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
        # we should issue a verification email here
        # https://wx.mail.qq.com/list/readtemplate?name=app_intro.html#/agreement/authorizationCode
        send_email(
            subject="确认您的注册账号",
            message=f"请点击以下链接以确认您的注册账号: http://localhost:3000/auth/verify-register/{token}",
            to_email=user.email,
        )
