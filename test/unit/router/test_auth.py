# 2024/6/17
# zhangzhong

from test.utils import my_client

from app.model import UserCreate


def test_basic_auth():
    user = my_client.register(
        user_create=UserCreate(
            name="zhangzhong",
            email="im.zhong@outlook.com",
            password="123456",
        )
    )
    print(user)
