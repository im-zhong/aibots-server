# 2024/6/13
# zhangzhong
# https://www.starlette.io/testclient/

import uuid
from test.utils import db_util

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app=app)


async def test_create_knowledge():
    bot = await db_util.create_random_bot()
    print(bot.id)
    knowledge = await db_util.create_temp_knowledge()
    bot_id = str(bot.id)
    # 我发现这么测试实在是太麻烦了
    # 我们难道就不能在测试的时候首先创建一批数据进行测试吗？
    response = client.post(
        url="/api/knowledge/create",
        json={
            "bot_id": str(bot_id),
            "topic": "temp",
        },
    )
    # assert response.status_code == 200
    # knowledge_id: str = response.json()
    # print(knowledge_id)


async def test_create_knowledge_by_upload_file():

    knowledge = await db_util.create_temp_knowledge()
    # 要首先创建知识 拿到他的kid
    # 才能在他下面创建知识点

    # with open(file=file_path, mode="rb") as f:
    #     response = client.post(
    #         url="/api/character/create",
    #         headers={"Authorization": f"{token.token_type} {token.access_token}"},
    #         # data={
    #         #     "name": "文档解读",
    #         #     "description": "文档解读",
    #         #     "avatar_url": avatar_url,
    #         #     "category": model.AIBotCategory.DOC_RAG.value,
    #         #     "uid": uid,
    #         #     # https://github.com/tiangolo/fastapi/issues/1536
    #         #     # "file": {"filename": "requirements.txt", "content": f.read()},
    #         # },
    #         data=model.CharacterCreate(
    #             name="小明",
    #             description="爱打游戏的大学生",
    #             avatar_url=avatar_url,
    #             category=model.AIBotCategory.DOC_RAG.value,
    #             uid=uid,
    #         ).model_dump(),
    #         # files={"file": ("requirements.txt", f, "text/plain")},
    #         files={"file": ("requirements.txt", f, "text/plain")},
    #     )

    file = (
        "/Users/zhangzhong/src/aibots/aibots-server/test/unit/router/test_knowledge.py"
    )
    with open(file=file, mode="rb") as f:
        response = client.post(
            url="/api/knowledge/upload-file",
            data={
                # "bot_id": "1",
                "knowledge_id": str(knowledge.id),
            },
            files={"file": ("test_knowledge.py", f, "text/plain")},
        )
    assert response.status_code == 200
    knowledge_id: str = response.json()
    print(knowledge_id)


def test_create_knowledge_point_by_upload_url():
    response = client.post(
        url="/api/knowledge/upload",
        json={
            "bot_id": "1",
            "knowledge_id": "2",
            "url": "https://www.baidu.com",
        },
    )
    assert response.status_code == 200
    knowledge_id: str = response.json()
    print(knowledge_id)
