# 2024/5/13
# zhangzhong
# https://docs.sqlalchemy.org/en/20/tutorial/orm_data_manipulation.html

import uuid
from datetime import datetime

from fastapi_users.db import SQLAlchemyBaseUserTableUUID, SQLAlchemyUserDatabase
from pydantic import BaseModel
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.common.conf import conf
from app.model import BotCreate, ChatCreate, KnowledgeCreate, KnowledgePointCreate

from .schema import (
    BaseSchema,
    BotSchema,
    ChatSchema,
    KnowledgePointSchema,
    KnowledgeSchema,
    MessageSchema,
    UserSchema,
)

engine = create_async_engine(
    url=conf.postgres_url,
    # https://stackoverflow.com/questions/75252097/fastapi-testing-runtimeerror-task-attached-to-a-different-loop
    # https://github.com/encode/starlette/issues/1315
    poolclass=NullPool,
)
async_session_maker = async_sessionmaker(bind=engine, expire_on_commit=False)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(BaseSchema.metadata.drop_all)
        await conn.run_sync(BaseSchema.metadata.create_all)


# TODO: 因为fastapiusers使用了async 所以我们的数据库实现和测试都要重写
# I have an idea, 我们的这个DatabaseService可以继承fastapiusers 的那个呀
# 这样很多函数就不需要重复的写了，然后又可以加上其他的数据库操作 完美！
# 不行，他的很多函数名字起的不好，我们还是得给他包装一下
class Database:
    # 我懂了，把session的创建和对数据的操作解开
    # 也就是database服务的创建传入一个session即可
    # 就想fastapiusers那样实现就ok
    def __init__(self, session: AsyncSession):
        # create a session by my self
        # self._session = SessionLocal()
        # 但是在这里创建好像不太行？因为session需要在一个 async context manager里面创建才行
        # 所以要在一个单独的方法里面创建
        #
        self.session = session
        self.user_db = SQLAlchemyUserDatabase(
            session=session,
            user_table=UserSchema,
        )

    # users
    # https://docs.sqlalchemy.org/en/20/tutorial/orm_data_manipulation.html#inserting-rows-using-the-orm-unit-of-work-pattern
    # def create_user(self, create: UserCreate) -> UserSchema:
    #     user = UserSchema(**create.model_dump())
    #     self._session.add(instance=user)
    #     self._session.commit()
    #     return user
    #
    # async def get_user_count(self) -> int:
    #     return self.session.query(UserSchema).filter_by(is_deleted=False).count()
    #
    # https://docs.sqlalchemy.org/en/20/tutorial/orm_data_manipulation.html#getting-objects-by-primary-key-from-the-identity-map
    # async def get_user(self, user_id: int) -> UserSchema | None:
    #     return await self.user_db.get(id=user_id)
    #
    # https://docs.sqlalchemy.org/en/20/tutorial/orm_data_manipulation.html#updating-orm-objects-using-the-unit-of-work-pattern
    # def update_user_profile(self, id: int, update: UserUpdate) -> UserSchema:
    #     # db_user = self._db.query( User).filter( User. id ==  id).first()
    #     # scalar_one: Return exactly one scalar result or raise an exception.
    #     user = self.get_user(id=id)
    #     for key, value in update.model_dump().items():
    #         if value is not None:
    #             setattr(user, key, value)
    #     self._session.commit()
    #     return user
    #
    # def update_user_password(self, id: int, password: str) -> UserSchema:
    #     user = self.get_user(id=id)
    #     user.password = password
    #     self._session.commit()
    #     return user
    #
    # # https://docs.sqlalchemy.org/en/20/tutorial/orm_data_manipulation.html#deleting-orm-objects-using-the-unit-of-work-pattern
    # def delete_user(self, id: int) -> None:
    #     user = self._session.execute(
    #         select(UserSchema).filter_by(id=id)
    #     ).scalar_one_or_none()
    #     if user:
    #         user.is_deleted = True
    #     self._session.commit()
    #
    # def get_users(self, offset: int, limit: int) -> list[UserSchema]:
    #     users = (
    #         self._session.execute(
    #             select(UserSchema)
    #             .filter_by(is_deleted=False)
    #             # https://stackoverflow.com/questions/4186062/sqlalchemy-order-by-descending
    #             .order_by(UserSchema.created_at.desc())
    #             .offset(offset)
    #             .limit(limit)
    #         )
    #         .scalars()
    #         .all()
    #     )
    #     return [u for u in users]
    #
    async def create_bot(self, bot_create: BotCreate) -> BotSchema:
        bot_dict = bot_create.model_dump()
        # bot_dict["knowledge_id"] = str(uuid.uuid4())
        # bot_dict["category"] = "chat_bot"
        # bot_dict["user_id"] = "f3e60362-40cc-463f-8f69-b0c8cd3a0b9d"
        # bot_dict.pop("knowledges")
        bot = BotSchema(**bot_dict)
        async with self.session.begin():
            self.session.add(bot)
            await self.session.commit()
        await self.session.refresh(bot)
        return bot

    async def create_knowledge(
        self, knowledge_create: KnowledgeCreate
    ) -> KnowledgeSchema:
        knowledge = KnowledgeSchema(**knowledge_create.model_dump())
        async with self.session.begin():
            self.session.add(knowledge)
            await self.session.commit()
        await self.session.refresh(knowledge)
        return knowledge

    async def create_knowledge_point(
        self, knowledge_point_create: KnowledgePointCreate
    ) -> KnowledgePointSchema:
        knowledge_point = KnowledgePointSchema(**knowledge_point_create.model_dump())
        async with self.session.begin():
            self.session.add(knowledge_point)
            await self.session.commit()
        await self.session.refresh(knowledge_point)
        return knowledge_point

    #
    # # TODO:
    # # 等真的把这些东西写出来，确实发现id这个名字不好
    # # 因为你会发现这个文件里面有太多的id 你一眼看过去根本不知道他表示的是什么
    # # 而是需要有明确的前缀
    # # 如果一个字段名字是自解释的，那是非常好的名字，如果一个名字还需要看表名才知道到底是什么
    # # 而且这个名字在不同的表里面重复出现，那么当然就不是一个好名字，很容易写错啊！！！
    # # 所以纯粹的使用id作为名字是一个非常差的设计！
    # # 终于论证出来了
    # def delete_bot(self, id: int) -> None:
    #     bot = self._session.execute(
    #         select(BotSchema).filter_by(id=id)
    #     ).scalar_one_or_none()
    #     if bot:
    #         bot.is_deleted = True
    #     self._session.commit()
    #
    # def get_bot(self, id: int) -> BotSchema:
    #     return self._session.get_one(entity=BotSchema, ident=id)
    #
    # def get_bot_count(self) -> int:
    #     return self._session.query(BotSchema).filter_by(is_deleted=False).count()
    #
    # def get_user_bot_count(self, user_id: int) -> int:
    #     return (
    #         self._session.query(BotSchema)
    #         .filter_by(user_id=user_id, is_deleted=False)
    #         .count()
    #     )
    #
    # # chats
    async def create_chat(self, chat_create: ChatCreate) -> ChatSchema:
        chat = ChatSchema(**chat_create.model_dump())
        async with self.session.begin():
            self.session.add(chat)
            await self.session.commit()
        await self.session.refresh(chat)
        return chat

    #
    # def delete_chat(self, chat_id: int) -> None:
    #     db_chat = self._session.execute(
    #         select(ChatSchema).filter_by(chat_id=chat_id)
    #     ).scalar_one_or_none()
    #     if db_chat:
    #         # self._db.delete(db_chat)
    #         db_chat.is_deleted = True
    #         self._session.commit()
    #
    # def get_chat(self, chat_id: int) -> ChatSchema:
    #     db_chat = self._session.get(ChatSchema, chat_id)
    #     return db_chat
    #
    # # content
    # def create_message(self, create: MessageCreate) -> MessageSchema:
    #     message = MessageSchema(**create.model_dump())
    #     self._session.add(message)
    #     self._session.commit()
    #     return message
