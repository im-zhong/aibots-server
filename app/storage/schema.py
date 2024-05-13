# 2024/5/13
# zhangzhong
# https://www.sqlalchemy.org/
# https://docs.sqlalchemy.org/en/20/tutorial/metadata.html#declaring-mapped-classes

from datetime import datetime

from sqlalchemy import ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column, relationship, sessionmaker

from app.common import conf
from app.model import Role

# database engine
# Create a database URL for SQLAlchemy¶
# This is the main line that you would have to modify if you wanted to use a different database.
# SQLALCHEMY_DATABASE_URL = conf.get_postgres_sqlalchemy_database_url()
# pool maintain the connections to database
# when the session need to issue a sql, it retrieves a connection from this pool
# and until the transaction related to the session is commit or rollback, this connection will end and returned to the poll
# and session is not thread-safe or async-safe, so we need to add the pool_size
engine = create_engine(url=conf.postgres_url, pool_size=32)

# class factory
# configured to create instances of Session bound to your specific database engine
# Each instance of SessionLocal represents a standalone conversation (or session) with the database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# base model like pydantic?
# Later we will inherit from this class to create each of the database models or classes (the ORM models):
Base = declarative_base()

# In a very simplistic way create the database tables:
# https://fastapi.tiangolo.com/tutorial/sql-databases/#alembic-note


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    name: Mapped[str] = mapped_column(unique=True)
    role: Mapped[str] = mapped_column(default=Role.USER.value)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now())
    password: Mapped[str] = mapped_column()
    is_deleted: Mapped[bool] = mapped_column(default=False)

    bots: Mapped[list["Bot"]] = relationship(back_populates="associated_user")
    chats: Mapped[list["Chat"]] = relationship(back_populates="associated_user")

    def is_admin(self) -> bool:
        return self.role == Role.ADMIN.value


class Bot(Base):
    __tablename__ = "bots"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    name: Mapped[str] = mapped_column(index=True)
    description: Mapped[str] = mapped_column()
    category: Mapped[str] = mapped_column()

    created_at: Mapped[datetime] = mapped_column(default=datetime.now())
    is_deleted: Mapped[bool] = mapped_column(default=False)
    is_shared: Mapped[bool] = mapped_column(default=False)
    knowledge_id: Mapped[str] = mapped_column(default="")
    memory_id: Mapped[str] = mapped_column(default="")

    associated_user: Mapped[User] = relationship(back_populates="bots")


class Chat(Base):
    __tablename__ = "chats"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    bot_id: Mapped[int] = mapped_column(ForeignKey("bots.id"))
    create_at: Mapped[datetime] = mapped_column(default=datetime.now())
    is_deleted: Mapped[bool] = mapped_column(default=False)

    associated_user: Mapped[User] = relationship(back_populates="chats")
    messages: Mapped[list["Message"]] = relationship(back_populates="associated_chat")


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    chat_id: Mapped[int] = mapped_column(ForeignKey("chats.id"))
    sender: Mapped[str] = mapped_column()
    content: Mapped[str] = mapped_column()
    images: Mapped[str] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=datetime.now())

    associated_chat: Mapped[Chat] = relationship(back_populates="messages")
