# 2024/6/15
# zhangzhong

# vector_store能干嘛呢？不就是读取一个文件，拿到一个id
# 然后调用embedding的方法， 然后把这个文件给保存起来吗？
# 他的入口应该就是一个path_or_url, 因为他内部可以根据这个判断是什么loader
# 入参没有必要是一个list 因为外部也不会用list来调用 写成list会让处理逻辑变得复杂
# okok
# TODO: 现在问题来了，我怎么知道这些数据确实插入到向量数据库中了呢

from test.utils import db_util

from app.storage.vector_store import vector_store


async def test_vector_store_load_plain_text():
    knowledge = await db_util.create_temp_knowledge()
    file = "/Users/zhangzhong/src/aibots/aibots-server/test/unit/storage/test_vector_store.py"

    await vector_store.add_knowledge_point(
        knowledge_id=str(knowledge.id), file_or_url=file
    )


async def test_vector_sotre_load_web_page():
    knowledge = await db_util.create_temp_knowledge()
    url = "https://python.langchain.com/v0.2/docs/integrations/vectorstores/qdrant/"

    await vector_store.add_knowledge_point(
        knowledge_id=str(knowledge.id), file_or_url=url
    )
