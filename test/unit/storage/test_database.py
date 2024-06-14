# 2024/5/13
# zhangzhong
# 以为数据库全部改成异步的了 所以测试也要改成异步的

import uuid
from test.utils import db_util, random_bot, random_character_category

from app.model import BotCreate, ChatCreate, UserCreate, UserUpdate
from app.storage.database import init_db
from app.storage.schema import (
    BaseSchema,
    BotSchema,
    ChatSchema,
    MessageSchema,
    UserSchema,
)

# TODO: 这句话必须在运行所有代码之前运行 否则就会出错
# 这显然不合理呀
# 现在的单元测试写的不好，因为测试之间竟然有依赖关系，这显然是不对的
# BaseSchema.metadata.create_all(bind=engine)


async def test_init_db():
    # how to drop all the table?
    await init_db()


async def test_create_update_delete_user():
    user = await db_util.create_random_user()
    print(user)

    # new_username = str(uuid.uuid4())
    # new_description = str(uuid.uuid4())
    # new_user = db.update_user_profile(
    #     id=user.id,  # 卧槽啊，果然就没有type hint error了
    #     update=UserUpdate(
    #         name=new_username,
    #         # avatar_description=new_description,
    #         # avatar_url="avatar url",
    #     ),
    # )
    # assert new_user.name == new_username
    # assert new_user.password == user.password
    # assert new_user.avatar_description == new_description

    # db.delete_user(id=user.id)
    # user = db.get_user(id=user.id)
    # assert user.is_deleted


async def test_create_update_delete_character():
    # db = Database()
    # db_util = DatabaseUtil()
    # user = db_util.create_user()
    # bot = db_util.create_bot(user=user)

    # db.delete_bot(id=bot.id)
    # bot = db.get_bot(id=bot.id)
    # assert bot.is_deleted
    bot = db_util.create_random_bot(user=await db_util.create_random_user())
    print(bot)


async def test_chat():
    # db = Database()
    # db_util = DatabaseUtil()
    # user = db_util.create_user()
    # bot = db_util.create_bot(user=user)
    # chat = db_util.create_chat(user=user, bot=bot)

    # db.create_message(
    #     create=MessageCreate(
    #         chat_id=chat.id,
    #         content="test",
    #         sender=MessageSender.HUMAN,
    #     )
    # )
    # db.create_message(
    #     create=MessageCreate(
    #         chat_id=chat.id,
    #         content="test",
    #         sender=MessageSender.AI,
    #     )
    # )
    # print(chat.messages)
    user = await db_util.create_random_user()
    bot = await db_util.create_random_bot(user=user)
    chat = await db_util.create_random_chat(user=user, bot=bot)
    print(chat)
