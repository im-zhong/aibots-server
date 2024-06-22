# 2024/5/13
# zhangzhong
# https://www.sqlalchemy.org/
# https://docs.sqlalchemy.org/en/20/tutorial/metadata.html#declaring-mapped-classes
# https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html

import uuid
from datetime import datetime
from uuid import UUID

from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from fastapi_users_db_sqlalchemy.generics import GUID
from sqlalchemy import ForeignKey
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class BaseSchema(AsyncAttrs, DeclarativeBase):
    pass


class UserSchema(SQLAlchemyBaseUserTableUUID, BaseSchema):
    __tablename__ = "users"

    name: Mapped[str] = mapped_column()
    avatar: Mapped[str] = mapped_column(default="")
    created_at: Mapped[datetime] = mapped_column(default=datetime.now())
    is_deleted: Mapped[bool] = mapped_column(default=False)

    agents: Mapped[list["AgentSchema"]] = relationship(back_populates="associated_user")
    chats: Mapped[list["ChatSchema"]] = relationship(back_populates="associated_user")


class AgentSchema(BaseSchema):
    __tablename__ = "agents"

    id: Mapped[UUID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    name: Mapped[str] = mapped_column(index=True)
    avatar: Mapped[str] = mapped_column(default="")
    description: Mapped[str] = mapped_column()
    # category: Mapped[str] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=datetime.now())
    is_deleted: Mapped[bool] = mapped_column(default=False)
    is_shared: Mapped[bool] = mapped_column(default=False)
    # knowledges: Mapped[list[str]] = mapped_column(default=[])
    memory_id: Mapped[str] = mapped_column(default="")
    prompt: Mapped[str] = mapped_column(default="")
    web_search: Mapped[bool] = mapped_column(default=False)
    painting: Mapped[bool] = mapped_column(default=False)
    multi_model: Mapped[bool] = mapped_column(default=False)

    associated_user: Mapped[UserSchema] = relationship(back_populates="agents")
    # knowledges: Mapped[list["KnowledgeSchema"]] = relationship(
    #     back_populates="associated_bot"
    # )

    agent_knowledges: Mapped[list["AgentKnowledgeSchema"]] = relationship(
        back_populates="associated_agent"
    )


class ChatSchema(BaseSchema):
    __tablename__ = "chats"

    id: Mapped[UUID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    agent_id: Mapped[UUID] = mapped_column(ForeignKey("agents.id"))
    create_at: Mapped[datetime] = mapped_column(default=datetime.now())
    is_deleted: Mapped[bool] = mapped_column(default=False)

    associated_user: Mapped[UserSchema] = relationship(back_populates="chats")
    messages: Mapped[list["MessageSchema"]] = relationship(
        back_populates="associated_chat"
    )


class MessageSchema(BaseSchema):
    __tablename__ = "messages"

    id: Mapped[UUID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    chat_id: Mapped[UUID] = mapped_column(ForeignKey("chats.id"))
    sender: Mapped[str] = mapped_column()
    content: Mapped[str] = mapped_column()
    images: Mapped[str] = mapped_column(default="")
    created_at: Mapped[datetime] = mapped_column(default=datetime.now())

    associated_chat: Mapped[ChatSchema] = relationship(back_populates="messages")


class KnowledgeSchema(BaseSchema):
    __tablename__ = "knowledges"

    id: Mapped[UUID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    topic: Mapped[str] = mapped_column()
    # bot_id: Mapped[UUID] = mapped_column(ForeignKey("bots.id"))

    # associated_bot: Mapped[BotSchema] = relationship(back_populates="knowledges")
    points: Mapped[list["KnowledgePointSchema"]] = relationship(
        back_populates="associated_knowledge"
    )
    agent_knowledges: Mapped[list["AgentKnowledgeSchema"]] = relationship(
        back_populates="associated_knowledge"
    )


class KnowledgePointSchema(BaseSchema):
    __tablename__ = "knowledge_points"

    id: Mapped[UUID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    knowledge_id: Mapped[UUID] = mapped_column(ForeignKey("knowledges.id"))
    # category: Mapped[str] = mapped_column()
    path_or_url: Mapped[str] = mapped_column()

    associated_knowledge: Mapped[KnowledgeSchema] = relationship(
        back_populates="points"
    )

    def is_url(self) -> bool:
        return "http" in self.path_or_url


# 果然是不行的
# 但是其实也简单
# 我们真正需要做的就是提供两个函数
# 一个是向某个agent添加某个知识
# 另一个是获取某个agent的所有知识
# 写两个函数就ok了呀
# 其实就是做一个join罢了
# 还是写一下吧 扩充一下技术点
class AgentKnowledgeSchema(BaseSchema):
    __tablename__ = "agent_knowledges"

    id: Mapped[UUID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    agent_id: Mapped[UUID] = mapped_column(ForeignKey("agents.id"))
    knowledge_id: Mapped[UUID] = mapped_column(ForeignKey("knowledges.id"))

    # relatioinship是双向的
    # 也就是说，我们也需要在agent和knowledge表中添加这些字段
    # 好像我只需要写python代码就可以变成join啊 这个太简单了
    associated_agent: Mapped[AgentSchema] = relationship(
        back_populates="agent_knowledges"
    )
    associated_knowledge: Mapped[KnowledgeSchema] = relationship(
        back_populates="agent_knowledges"
    )
