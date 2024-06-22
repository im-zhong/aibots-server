# 2024/5/22
# zhangzhong

from test.utils import db_util, my_client

from fastapi.testclient import TestClient

from app.main import app
from app.model import ChatCreate
from app.model.chat import ChatMessage

uid = 1
cid = 2


async def test_chat():

    user = await db_util.create_random_user()
    bot = await db_util.create_random_bot()

    # you should create a chat first
    # 应该像db_util那样，封装一个 client_util
    # 我们在此之上 非常简单的调用系统提供的API
    # 这样就非常方便测试
    chat_id = my_client.create_chat(
        chat_create=ChatCreate(
            user_id=str(user.id),
            agent_id=str(bot.id),
        )
    )

    with my_client.client.websocket_connect(
        url=f"/ws/chat?chat_id={chat_id}"
    ) as websocket:
        websocket.send_json(
            data=ChatMessage(
                sender=uid,
                receiver=cid,
                is_end_of_stream=True,
                content="hello",
            ).model_dump()
        )
        # cause now we use stream
        # so we should receive the reponse until its end of stream
        content = ""
        while True:
            data = websocket.receive_json()
            print(data)
            response_message = ChatMessage(**data)
            content += response_message.content
            if response_message.is_end_of_stream:
                break
        print(content)

        websocket.send_json(
            data=ChatMessage(
                sender=uid,
                receiver=cid,
                is_end_of_stream=True,
                content="how are you",
            ).model_dump()
        )

        content = ""
        while True:
            data = websocket.receive_json()
            print(data)
            response_message = ChatMessage(**data)
            content += response_message.content
            if response_message.is_end_of_stream:
                break
        print(content)
