# 2024/5/13
# zhangzhong

import uuid
from test.utils import DatabaseUtil, random_bot, random_character_category

from app.model import (
    BotCreate,
    ChatCreate,
    MessageCreate,
    MessageSender,
    UserCreate,
    UserUpdate,
)
from app.storage.database import DatabaseService, schema
from app.storage.schema import (
    Base,
    BotSchema,
    ChatSchema,
    MessageSchema,
    UserSchema,
    engine,
)

# TODO: 这句话必须在运行所有代码之前运行 否则就会出错
# 这显然不合理呀
# 现在的单元测试写的不好，因为测试之间竟然有依赖关系，这显然是不对的
Base.metadata.create_all(bind=engine)


def test_create_update_delete_user():
    db = DatabaseService()
    db_util = DatabaseUtil()
    user = db_util.create_user()
    print(user.id)

    new_username = str(uuid.uuid4())
    new_description = str(uuid.uuid4())
    new_user = db.update_user(
        id=user.id,  # 卧槽啊，果然就没有type hint error了
        update=UserUpdate(
            name=new_username,
            # avatar_description=new_description,
            # avatar_url="avatar url",
        ),
    )
    assert new_user.name == new_username
    assert new_user.password == user.password
    # assert new_user.avatar_description == new_description

    db.delete_user(id=user.id)
    user = db.get_user(id=user.id)
    assert user.is_deleted


def test_create_update_delete_character():
    db = DatabaseService()
    db_util = DatabaseUtil()
    user = db_util.create_user()
    bot = db_util.create_bot(user=user)

    db.delete_bot(id=bot.id)
    bot = db.get_bot(id=bot.id)
    assert bot.is_deleted


def test_chat():
    db = DatabaseService()
    db_util = DatabaseUtil()
    user = db_util.create_user()
    bot = db_util.create_bot(user=user)
    chat = db_util.create_chat(user=user, bot=bot)

    db.create_message(
        create=MessageCreate(
            chat_id=chat.id,
            content="test",
            sender=MessageSender.HUMAN,
        )
    )
    db.create_message(
        create=MessageCreate(
            chat_id=chat.id,
            content="test",
            sender=MessageSender.AI,
        )
    )
    print(chat.messages)
