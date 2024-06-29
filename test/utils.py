# 2024/5/13
# zhangzhong


import base64
import random
import uuid
from datetime import datetime
from io import BytesIO

import redis.asyncio
from fastapi.testclient import TestClient
from PIL import Image

from app.common.conf import conf
from app.main import app

# 但是你要真这样引用起来还是挺麻烦的
# 不如还是从 app.model 里面进行全部的引用，但是在实现上我们进行一个区分
# from app.model.bot import BotCreate
# # from app.model.chat import ChatCreate,
# from app.model.user import UserCreate
from app.model import AgentCreate, ChatCreate, KnowledgeCreate, UserCreate, UserOut
from app.storage.database import AsyncSession, Database, async_session_maker
from app.storage.schema import (
    AgentKnowledgeSchema,
    AgentSchema,
    ChatSchema,
    KnowledgeSchema,
    MessageSchema,
    UserSchema,
)
from app.tool.painting import dalle

myredis = redis.asyncio.from_url(url=conf.redis_url, decode_responses=True)

# model定义为什么要单独分一个模块呢？
# 为什么这些定义不能和直接使用它的地方紧密的结合起来呢？
# 算了，这个东西的定义同时被两个地方使用 router + database
# 还是放到一个单独的模块进行定义
# 关键问题时这些东西应该放到那个模块？
# 其实也很难说清


# client = TestClient(app)


def default_character_avatar_url() -> str:
    url = "http://localhost:9000/test/00af8ddb-3f65-5363-91c2-d9dbff86f299_0.png"
    return url


def random_character_category() -> str:
    return random.choice(["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"])


def random_email() -> str:
    return f"{random_name()}@test.com"


def random_name() -> str:
    return str(uuid.uuid4())


def random_bot(user_id: uuid.UUID) -> AgentCreate:
    return AgentCreate(
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
    async def create_random_bot(user: UserSchema | None = None) -> AgentSchema:
        if user is None:
            user = await DBUtil.create_random_user()
        async with async_session_maker() as session:
            return await Database(session=session).create_agent(
                agent_create=random_bot(user_id=user.id)
            )

    @staticmethod
    async def create_random_chat(
        user: UserSchema | None = None, bot: AgentSchema | None = None
    ) -> ChatSchema:
        if user is None:
            user = await DBUtil.create_random_user()
        if bot is None:
            bot = await DBUtil.create_random_bot(user=user)
        async with async_session_maker() as session:
            return await Database(session=session).create_chat(
                chat_create=ChatCreate(
                    user_id=str(user.id),
                    agent_id=str(bot.id),
                )
            )

    @staticmethod
    async def create_temp_knowledge(
        user: UserSchema | None = None, bot: AgentSchema | None = None
    ) -> KnowledgeSchema:
        if user is None:
            user = await DBUtil.create_random_user()
        if bot is None:
            bot = await DBUtil.create_random_bot(user=user)
        async with async_session_maker() as session:
            return await Database(session=session).create_knowledge(
                knowledge_create=KnowledgeCreate(
                    # agent_id=bot.id,
                    topic="temp",
                )
            )

    @staticmethod
    async def add_knowledge_to_agent(
        agent: AgentSchema, knowledge: KnowledgeSchema | None
    ) -> AgentKnowledgeSchema:
        if knowledge is None:
            knowledge = await DBUtil.create_temp_knowledge()
        async with async_session_maker() as session:
            return (
                await Database(session=session).add_knowledges_to_agent(
                    agent_id=agent.id,
                    knowledge_ids=[knowledge.id],
                )
            )[0]

    @staticmethod
    async def get_knowledges_of_agent(agent: AgentSchema) -> list[KnowledgeSchema]:
        async with async_session_maker() as session:
            return await Database(session=session).get_knowledges_of_agent(
                agent_id=agent.id,
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


class MyTestClient:
    # 为了方便测试，我们应该直接将api的返回结果序列化成pydantic model
    # 以及，发出任务错误时，直接抛出异常
    def __init__(self) -> None:
        self.client = TestClient(app=app)
        # self.cookie: dict | None = None

    def create_chat(self, chat_create: ChatCreate) -> str:
        response = self.client.post(
            url="/api/chat/create",
            json=chat_create.model_dump(),
        )
        assert response.status_code == 200, f"create chat failed: {response.text}"
        return response.json()

    # 我们还要写一个context manager 来模拟websocket chat

    # https://fastapi-users.github.io/fastapi-users/latest/usage/routes/
    def login(self, username: str, password: str):
        response = self.client.post(
            url="/api/auth/login",
            data={"username": username, "password": password},
        )
        # https://fastapi-users.github.io/fastapi-users/latest/configuration/authentication/transports/cookie/
        assert response.status_code == 204, f"login failed: {response.text}"
        # return response
        # we need to get the cookie in the header
        cookie = response.headers["set-cookie"]
        cookie_dict = {}
        for cookie in cookie.split(";"):
            if "=" in cookie:
                key, value = cookie.split("=", 1)
                cookie_dict[key.strip()] = value.strip()

        self.cookie = cookie_dict
        return cookie_dict

    def logout(self, cookie: dict):
        # if self.cookie is None:
        #     return
        key = "fastapiusersauth"
        value = cookie[key]
        response = self.client.post(
            url="/api/auth/logout",
            headers={"Cookie": f"{key}={value}"},
        )
        assert response.status_code == 204, f"logout failed: {response.text}"
        return response

    def register(self, user_create: UserCreate) -> UserOut:
        response = self.client.post(
            url="/api/auth/register",
            json=user_create.model_dump(),
        )
        assert response.status_code == 201, f"register failed: {response}"
        return UserOut(**response.json())

    async def request_verify_token(self, email: str) -> str | None:
        response = self.client.post(
            url="/api/auth/request-verify-token",
            json={"email": email},
        )
        assert response.status_code == 202, f"request verify token failed: {response}"
        # 正常来说，我们是拿不到这个token的，因为真正的token会发邮件给用户
        # 但是我们这里是测试，所以我们可以从数据库中直接读取token 返回
        # 这样就很方便测试了
        token = await myredis.get(name="my" + email)
        return token

    async def verify(self, token: str):
        response = self.client.post(
            url="/api/auth/verify",
            json={"token": token},
        )
        assert response.status_code == 200

    async def forgot_password(self, email: str) -> str:
        response = self.client.post(
            url="/api/auth/forgot-password",
            json={"email": email},
        )
        assert response.status_code == 202, f"forget password failed: {response}"
        token = await myredis.get(name="forgot-password" + email)
        return token

    async def reset_password(self, token: str, password: str):
        response = self.client.post(
            url="/api/auth/reset-password",
            json={"token": token, "password": password},
        )
        assert response.status_code == 200, f"reset password failed: {response}"


my_client = MyTestClient()


class PaintingTool:
    def __init__(self) -> None:
        pass

    def draw(self, prompt: str):
        # class ImagesResponse(BaseModel):
        # created: int
        # data: List[Image]

        # class Image(BaseModel):
        # b64_json: Optional[str] = None
        # """
        # The base64-encoded JSON of the generated image, if `response_format` is
        # `b64_json`.
        # """
        # revised_prompt: Optional[str] = None
        # """
        # The prompt that was used to generate the image, if there was any revision to the
        # prompt.
        # """
        # url: Optional[str] = None
        # """The URL of the generated image, if `response_format` is `url` (default)."""
        response = dalle(prompt=prompt)
        for image in response.data:
            #  print(image.b64_json)
            print(image.revised_prompt)
            if image.url:
                print(image.url)
            if image.b64_json:
                # Step 1: Decode the base64 string
                image_bytes = base64.b64decode(image.b64_json)

                # Step 2: Create an image from the decoded bytes
                image_data = BytesIO(image_bytes)
                image = Image.open(image_data)

                # Step 3: Save the image to a file
                # 咱们自动生成一些id吧，或者说可以用created这个充当id
                image.save(
                    fp=f"assets/images/{datetime.now().strftime(format="%d-%m-%Y-%H-%M-%S")}-{response.created}.png"
                )  # Specify your desired output image file name and format


painting_tool = PaintingTool()
