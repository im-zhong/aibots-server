# 2024/6/15
# zhangzhong

# vector_store能干嘛呢？不就是读取一个文件，拿到一个id
# 然后调用embedding的方法， 然后把这个文件给保存起来吗？
# 他的入口应该就是一个path_or_url, 因为他内部可以根据这个判断是什么loader
# 入参没有必要是一个list 因为外部也不会用list来调用 写成list会让处理逻辑变得复杂
# okok

from app.storage.vector_store import KnowledgeBase


async def test_vector_store_load_plain_text():
    pass
