# 2024/6/13
# zhangzhong

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app=app)


def test_create_knowledge():
    client.post(
        url="/api/knowledge/create",
        json={
            "bot_id": "1",
            "topic": "temp",
        },
    )


def test_create_knowledge_by_upload_file():
    response = client.post(
        url="/api/knowledge/upload",
        json={
            "bot_id": "1",
            "knowledge_id": "1",
            "file": "test/unit/test_data/test.txt",
        },
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
