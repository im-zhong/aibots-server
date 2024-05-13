# 2024/5/13
# zhangzhong
# https://docs.sqlalchemy.org/en/20/tutorial/orm_data_manipulation.html

from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.common.conf import conf
from app.model import (
    BotCategory,
    BotCreate,
    BotOut,
    ChatCreate,
    ChatMessage,
    ChatOut,
    MessageCreate,
    MessageOut,
    MessageSender,
    Role,
    UserCreate,
    UserPasswordUpdate,
    UserUpdate,
)

from . import schema
from .schema import BotSchema, ChatSchema, MessageSchema, SessionLocal, UserSchema


class DatabaseService:
    def __init__(self) -> None:
        # create a session by my self
        self._session = SessionLocal()

    def close(self):
        self._session.close()

    # users
    # https://docs.sqlalchemy.org/en/20/tutorial/orm_data_manipulation.html#inserting-rows-using-the-orm-unit-of-work-pattern
    def create_user(self, create: UserCreate) -> UserSchema:
        user = UserSchema(**create.model_dump())
        self._session.add(instance=user)
        self._session.commit()
        return user

    def get_user_count(self) -> int:
        return self._session.query(UserSchema).filter_by(is_deleted=False).count()

    # https://docs.sqlalchemy.org/en/20/tutorial/orm_data_manipulation.html#getting-objects-by-primary-key-from-the-identity-map
    def get_user(self, id: int) -> UserSchema:
        user = self._session.get(entity=UserSchema, ident=id)
        return user

    # https://docs.sqlalchemy.org/en/20/tutorial/orm_data_manipulation.html#updating-orm-objects-using-the-unit-of-work-pattern
    def update_user(self, id: int, update: UserUpdate) -> UserSchema:
        # db_user = self._db.query( User).filter( User. id ==  id).first()
        # scalar_one: Return exactly one scalar result or raise an exception.
        user = self.get_user(id=id)
        for key, value in update.model_dump().items():
            if value is not None:
                setattr(user, key, value)
        self._session.commit()
        return user

    def update_user_password(self, id: int, password: str) -> UserSchema:
        user = self.get_user(id=id)
        user.password = password
        self._session.commit()
        return user

    # https://docs.sqlalchemy.org/en/20/tutorial/orm_data_manipulation.html#deleting-orm-objects-using-the-unit-of-work-pattern
    def delete_user(self, id: int) -> None:
        user = self._session.execute(
            select(UserSchema).filter_by(id=id)
        ).scalar_one_or_none()
        if user:
            user.is_deleted = True
        self._session.commit()

    def get_users(self, offset: int, limit: int) -> list[UserSchema]:
        users = (
            self._session.execute(
                select(UserSchema)
                .filter_by(is_deleted=False)
                # https://stackoverflow.com/questions/4186062/sqlalchemy-order-by-descending
                .order_by(UserSchema.created_at.desc())
                .offset(offset)
                .limit(limit)
            )
            .scalars()
            .all()
        )
        return [u for u in users]

    def create_bot(self, create: BotCreate) -> BotSchema:
        # we did not include a primary key (i.e. an entry for the id column), since we would like to make use of the auto-incrementing primary key feature of the database,
        bot = BotSchema(**create.model_dump())
        self._session.add(bot)
        self._session.commit()
        return bot

    def delete_bot(self, id: int) -> None:
        bot = self._session.execute(
            select(BotSchema).filter_by(id=id)
        ).scalar_one_or_none()
        if bot:
            bot.is_deleted = True
        self._session.commit()

    def get_bot(self, id: int) -> BotSchema:
        return self._session.get_one(entity=BotSchema, ident=id)

    def get_bot_count(self) -> int:
        return self._session.query(BotSchema).filter_by(is_deleted=False).count()

    def get_user_bot_count(self, user_id: int) -> int:
        return (
            self._session.query(BotSchema)
            .filter_by(user_id=user_id, is_deleted=False)
            .count()
        )

    # chats
    def create_chat(self, chat_create: ChatCreate) -> ChatSchema:
        chat = ChatSchema(**chat_create.model_dump())
        self._session.add(chat)
        self._session.commit()
        return chat

    def delete_chat(self, chat_id: int) -> None:
        db_chat = self._session.execute(
            select(ChatSchema).filter_by(chat_id=chat_id)
        ).scalar_one_or_none()
        if db_chat:
            # self._db.delete(db_chat)
            db_chat.is_deleted = True
            self._session.commit()

    def get_chat(self, chat_id: int) -> ChatSchema:
        db_chat = self._session.get(ChatSchema, chat_id)
        return db_chat

    # content
    def create_message(self, create: MessageCreate) -> MessageSchema:
        message = MessageSchema(**create.model_dump())
        self._session.add(message)
        self._session.commit()
        return message
