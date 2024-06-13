# 2024/5/22
# zhangzhong
# https://fastapi.tiangolo.com/tutorial/background-tasks/


import asyncio
import os
import uuid
from typing import Annotated

import aiofiles
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Body,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
)

from app.common.conf import conf
from app.router.dependency import AsyncSession, get_db
from app.storage.database import DatabaseService, async_session_maker
from app.storage.vector_store import KnowledgeBase

knowledge = APIRouter(prefix="/api/knowledge", tags=["knowledge"])


# write a api for upload file


# I have an idea, 我们可以在上传知识的时候就直接处理知识
# 这样处理完的知识就直接存储在数据库里面了，我们也不需要专门找一个地方存放文件
# 直接放到向量数据库里面就行


async def create_knowledge(
    bot_id: str, knowledge_id: str, filename: str = None, url: str = None
):
    # 用户每次上传的都是一个个的知识点
    # 用户一次只能上传一个文件或者一个网页
    # 不对 在用户端是可以上传多个的
    # 但是实际上对应到的是多次的API调用
    # 在API着一层看起来，每次就是一个知识点
    # 每个知识可以是多个文件，但是应该属于同一个主题
    # 之后也可以在同主题上增加新的知识，也可以增加新的主题
    # TODO: vector store也可以做async，这样就不会阻塞了，太棒了！
    # https://python.langchain.com/v0.1/docs/modules/data_connection/vectorstores/#asynchronous-operations
    knowledge = KnowledgeBase(knowledge_id=knowledge_id, urls=[url], files=[filename])
    # 然后在数据库中添加知识
    # 要不还是把文件和url保留下来吧，后端可以做一个留存
    # 但是其实并没有什么用处就是了
    # asyncio.get_event_loop().create_task(knowledge.vector_store.create())
    async with async_session_maker() as session:
        db = DatabaseService(session=session)
        db.create_knowledge_point(
            knowledge_id=knowledge_id, path=filename if filename else url
        )
    pass


@knowledge.post("/create")
async def knowledge_create(
    bot_id: str = Body(..., description="bot id"),
    topic: str = Body(..., description="knowledge topic"),
    db: DatabaseService = Depends(get_db),
) -> str:
    knowledge = await db.create_knowledge(bot_id=bot_id, topic=topic)
    return str(knowledge.id)


# TODO: 改一下名字，上传文件和上传webpage的接口可以分开
# 毕竟后端处理起来也不一样，前端处理也不一样
@knowledge.post("/upload")
async def knowledge_upload(
    bot_id: Annotated[str, Form(description="bot id")],
    knowledge_id: Annotated[str, Form(description="knowledge id")],
    file: Annotated[UploadFile, File(description="knowledge file")],
):
    # knowledge_id = str(uuid.uuid4())
    filename = f"{knowledge_id}-{file.filename}"
    filename = os.path.join(conf.knowledge_file_base_dir, filename)
    file_length = 0
    async with aiofiles.open(file=filename, mode="wb") as out_file:
        chunk_size = 4096  # 4K
        while content := await file.read(size=chunk_size):
            await out_file.write(content)
            file_length += chunk_size // 1024
            if file_length > conf.max_file_length:
                raise ValueError(
                    f"File is too large, max file length is {conf.max_file_length // 1024}MB"
                )

    # TODO：1
    # 在拿到文件之后，我们还需要做生成知识库的一个处理
    # 但是，其实在拿到id之后，我们就已经可以返回了
    # 之后用户可以继续操作，而我们在后台处理生成知识库，插入数据库就ok啦
    # 这里或许可以使用fastapi的background task

    # TODO：2
    # 生成知识库的接口是什么，我写好了吗？
    # RetrievalFactory().
    create_knowledge(knowledge_id=knowledge_id, filename=filename)
    # return knowledge_id


@knowledge.post("/upload-webpage")
async def knowledge_upload_webpage(
    bot_id: Annotated[str, Form(description="bot id")],
    knowledge_id: Annotated[str, Form(description="knowledge id")],
    url: Annotated[str, Form(description="webpage url")],
    topic: Annotated[str, Form(description="knowledge topic")],
    background_tasks: BackgroundTasks,
    db: Annotated[DatabaseService, Depends(get_db)],
) -> str:
    # knowledge_id = str(uuid.uuid4())
    background_tasks.add_task(
        create_knowledge,
        knowledge_id=knowledge_id,
        url=url,
    )
    await db.create_knowledge(bot_id=bot_id, knowledge_id=knowledge_id, url=url)
    # 在数据库中添加相关词条
    return knowledge_id


# @knowledge.get("/list")
# async def knowledge_list() -> list[str]:
#     return os.listdir(conf.knowledge_file_base_dir)
