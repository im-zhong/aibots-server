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


class Base(AsyncAttrs, DeclarativeBase):
    pass


class UserSchema(SQLAlchemyBaseUserTableUUID, Base):
    __tablename__ = "users"

    name: Mapped[str] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=datetime.now())
    is_deleted: Mapped[bool] = mapped_column(default=False)

    bots: Mapped[list["BotSchema"]] = relationship(back_populates="associated_user")
    chats: Mapped[list["ChatSchema"]] = relationship(back_populates="associated_user")


class BotSchema(Base):
    __tablename__ = "bots"

    id: Mapped[UUID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    name: Mapped[str] = mapped_column(index=True)
    description: Mapped[str] = mapped_column()
    category: Mapped[str] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=datetime.now())
    is_deleted: Mapped[bool] = mapped_column(default=False)
    is_shared: Mapped[bool] = mapped_column(default=False)
    knowledge_id: Mapped[str] = mapped_column(default="")
    memory_id: Mapped[str] = mapped_column(default="")

    associated_user: Mapped[UserSchema] = relationship(back_populates="bots")
    associated_knowledges: Mapped[list["KnowledgeSchema"]] = relationship(
        back_populates="bot_id"
    )


class ChatSchema(Base):
    __tablename__ = "chats"

    id: Mapped[UUID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    bot_id: Mapped[UUID] = mapped_column(ForeignKey("bots.id"))
    create_at: Mapped[datetime] = mapped_column(default=datetime.now())
    is_deleted: Mapped[bool] = mapped_column(default=False)

    associated_user: Mapped[UserSchema] = relationship(back_populates="chats")
    messages: Mapped[list["MessageSchema"]] = relationship(
        back_populates="associated_chat"
    )


class MessageSchema(Base):
    __tablename__ = "messages"

    id: Mapped[UUID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    chat_id: Mapped[UUID] = mapped_column(ForeignKey("chats.id"))
    sender: Mapped[str] = mapped_column()
    content: Mapped[str] = mapped_column()
    images: Mapped[str] = mapped_column(default="")
    created_at: Mapped[datetime] = mapped_column(default=datetime.now())

    associated_chat: Mapped[ChatSchema] = relationship(back_populates="messages")


class KnowledgeSchema(Base):
    __tablename__ = "knowledges"

    id: Mapped[UUID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    topic: Mapped[str] = mapped_column()
    bot_id: Mapped[UUID] = mapped_column(ForeignKey("bots.id"))

    associated_points: Mapped[list["KnowledgePointSchema"]] = relationship(
        back_populates="knowledge_id"
    )


class KnowledgePointSchema(Base):
    __tablename__ = "knowledge_points"

    id: Mapped[UUID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    knowledge_id: Mapped[UUID] = mapped_column(ForeignKey("knowledges.id"))
    category: Mapped[str] = mapped_column()
    path: Mapped[str] = mapped_column()

    associated_knowledge: Mapped[KnowledgeSchema] = relationship(
        back_populates="associated_points"
    )
