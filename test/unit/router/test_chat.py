# 2024/5/22
# zhangzhong

from fastapi.testclient import TestClient

from app.main import app
from app.model.chat import ChatMessage

client = TestClient(app=app)


uid = 1
cid = 2


def test_chat():
    with client.websocket_connect(url="/ws/chat") as websocket:
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
