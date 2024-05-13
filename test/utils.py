# 2024/5/13
# zhangzhong


import random
import uuid

from fastapi.testclient import TestClient

from app.main import app
from app.model import BotCreate, ChatCreate, UserCreate
from app.storage.database import DatabaseService
from app.storage.schema import BotSchema, ChatSchema, MessageSchema, UserSchema

client = TestClient(app)


def default_character_avatar_url() -> str:
    url = "http://localhost:9000/test/00af8ddb-3f65-5363-91c2-d9dbff86f299_0.png"
    return url


def random_character_category() -> str:
    return random.choice(["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"])


def random_name() -> str:
    return str(uuid.uuid4())


def random_bot(user_id: int) -> BotCreate:
    return BotCreate(
        user_id=user_id,
        name="test",
        description="random character description",
        # avatar_url=default_character_avatar_url(),
        category=random_character_category(),
    )


# 我觉得真正该做的是写一个类
# 这个类可以提供一些随机的方法，比如随机的创建一个用户，然后返回他
# 这样我们就可以进行下一个测试


class DatabaseUtil:
    def __init__(self):
        self.db = DatabaseService()

    def create_user(self) -> UserSchema:
        name = str(uuid.uuid4())
        password = str(uuid.uuid4())
        description = str(uuid.uuid4())

        user = self.db.create_user(
            create=UserCreate(
                email=name,
                name=name,
                password=password,
            )
        )
        return user

    def create_bot(self, user: UserSchema) -> BotSchema:
        character = self.db.create_bot(create=random_bot(user_id=user.id))
        return character

    def create_chat(self, user: UserSchema, bot: BotSchema) -> ChatSchema:
        chat = self.db.create_chat(
            ChatCreate(
                user_id=user.id,
                bot_id=bot.id,
            )
        )
        return chat


# def create_random_user() -> UserSchema:
#     db = DatabaseService()
#     user_create = UserCreate(
#         email=random_name(),
#         name=random_name(),
#         password=random_name(),
#     )

#     prefix = "/api/user"
#     # 然后调用注册接口
#     response = client.post(
#         url=f"{prefix}/register",
#         json=user_create.model_dump(),
#     )
#     assert response.status_code == 200
#     user_out = model.UserOut(**response.json())

#     # get this user from db
#     # 注册完了返回什么东西?
#     return db.get_user(uid=user_out.uid)


# def user_login(username: str, password: str) -> model.Token:
#     # 不对，数据库里面的password是hash之后的，无法用来登录
#     prefix = "/api/user"
#     response = client.post(
#         url=f"{prefix}/login",
#         data={"username": username, "password": password},
#     )
#     assert response.status_code == 200
#     token = model.Token(**response.json())
#     return token
