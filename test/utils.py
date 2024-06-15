# 2024/5/13
# zhangzhong


import random
import uuid

from fastapi.testclient import TestClient

from app.main import app

# 但是你要真这样引用起来还是挺麻烦的
# 不如还是从 app.model 里面进行全部的引用，但是在实现上我们进行一个区分
# from app.model.bot import BotCreate
# # from app.model.chat import ChatCreate,
# from app.model.user import UserCreate
from app.model import BotCreate, ChatCreate, KnowledgeCreate, UserCreate
from app.storage.database import AsyncSession, Database, async_session_maker
from app.storage.schema import (
    BotSchema,
    ChatSchema,
    KnowledgeSchema,
    MessageSchema,
    UserSchema,
)

# model定义为什么要单独分一个模块呢？
# 为什么这些定义不能和直接使用它的地方紧密的结合起来呢？
# 算了，这个东西的定义同时被两个地方使用 router + database
# 还是放到一个单独的模块进行定义
# 关键问题时这些东西应该放到那个模块？
# 其实也很难说清


client = TestClient(app)


def default_character_avatar_url() -> str:
    url = "http://localhost:9000/test/00af8ddb-3f65-5363-91c2-d9dbff86f299_0.png"
    return url


def random_character_category() -> str:
    return random.choice(["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"])


def random_email() -> str:
    return f"{random_name()}@test.com"


def random_name() -> str:
    return str(uuid.uuid4())


def random_bot(user_id: uuid.UUID) -> BotCreate:
    return BotCreate(
        user_id=user_id,
        name="test",
        description="random character description",
        # avatar_url=default_character_avatar_url(),
        # 以后不在有category 因为所有的bot都是agent，有区别的只有他们的能力
        # category=random_character_category(),
    )


# 我觉得真正该做的是写一个类
# 这个类可以提供一些随机的方法，比如随机的创建一个用户，然后返回他
# 这样我们就可以进行下一个测试


class DBUtil:
    # TIP: 通过这个函数创建的user无法登录
    @staticmethod
    async def create_random_user() -> UserSchema:
        async with async_session_maker() as session:
            return await Database(session=session).user_db.create(
                create_dict={
                    "name": random_name(),
                    "email": random_email(),
                    "hashed_password": random_name(),
                }
            )

    @staticmethod
    async def create_random_bot(user: UserSchema | None = None) -> BotSchema:
        if user is None:
            user = await DBUtil.create_random_user()
        async with async_session_maker() as session:
            return await Database(session=session).create_bot(
                bot_create=random_bot(user_id=user.id)
            )

    @staticmethod
    async def create_random_chat(
        user: UserSchema | None = None, bot: BotSchema | None = None
    ) -> ChatSchema:
        if user is None:
            user = await DBUtil.create_random_user()
        if bot is None:
            bot = await DBUtil.create_random_bot(user=user)
        async with async_session_maker() as session:
            return await Database(session=session).create_chat(
                chat_create=ChatCreate(
                    user_id=user.id,
                    bot_id=bot.id,
                )
            )

    @staticmethod
    async def create_temp_knowledge(
        user: UserSchema | None = None, bot: BotSchema | None = None
    ) -> KnowledgeSchema:
        if user is None:
            user = await DBUtil.create_random_user()
        if bot is None:
            bot = await DBUtil.create_random_bot(user=user)
        async with async_session_maker() as session:
            return await Database(session=session).create_knowledge(
                knowledge_create=KnowledgeCreate(
                    bot_id=bot.id,
                    topic="temp",
                )
            )


db_util = DBUtil()

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
