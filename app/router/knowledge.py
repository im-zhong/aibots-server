# 2024/5/22
# zhangzhong
# https://fastapi.tiangolo.com/tutorial/background-tasks/


import asyncio
import os
import uuid
from typing import Annotated
from uuid import UUID

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

# TODO: 其实category不是必须的，因为path还是url可以通过 local:// 和 http:// 来区分
# 而文件的种类可以通过后缀来区分 所以实际上不需要category
from app.model import KnowledgeCreate, KnowledgePointCategory, KnowledgePointCreate
from app.router.dependency import AsyncSession, get_db
from app.storage.database import Database, async_session_maker
from app.storage.schema import KnowledgePointSchema
from app.storage.vector_store import vector_store

# from app.storage.vector_store import KnowledgeBase

knowledge = APIRouter(prefix="/api/knowledge", tags=["knowledge"])


# write a api for upload file


# I have an idea, 我们可以在上传知识的时候就直接处理知识
# 这样处理完的知识就直接存储在数据库里面了，我们也不需要专门找一个地方存放文件
# 直接放到向量数据库里面就行


async def create_knowledge_indexing(knowledge_point: KnowledgePointSchema):
    # 用户每次上传的都是一个个的知识点
    # 用户一次只能上传一个文件或者一个网页
    # 不对 在用户端是可以上传多个的
    # 但是实际上对应到的是多次的API调用
    # 在API着一层看起来，每次就是一个知识点
    # 每个知识可以是多个文件，但是应该属于同一个主题
    # 之后也可以在同主题上增加新的知识，也可以增加新的主题
    # TODO: vector store也可以做async，这样就不会阻塞了，太棒了！
    # # https://python.langchain.com/v0.1/docs/modules/data_connection/vectorstores/#asynchronous-operations
    # path_or_url = knowledge_point.path_or_url
    # if path_or_url.startswith(("www", "http")):
    #     url = path_or_url
    # else:
    #     file = path_or_url
    # knowledge = KnowledgeBase(
    #     knowledge_id=str(knowledge_point.knowledge_id),
    #     urls=[url],
    #     files=[file],
    # )
    # 然后在数据库中添加知识
    # 要不还是把文件和url保留下来吧，后端可以做一个留存
    # 但是其实并没有什么用处就是了
    # asyncio.get_event_loop().create_task(knowledge.vector_store.create())
    # async with async_session_maker() as session:
    #     db = Database(session=session)
    #     db.create_knowledge_point(
    #         knowledge_point_create=KnowledgePointCreate(knowledge_id=knowledge_id)
    #         knowledge_id=knowledge_id, path=filename if filename else url
    #     )
    await vector_store.add_knowledge_point(
        knowledge_id=str(knowledge_point.knowledge_id),
        file_or_url=knowledge_point.path_or_url,
    )


@knowledge.post(path="/create")
async def create_knowledge(
    knowledge_create: KnowledgeCreate, db: Database = Depends(get_db)
) -> str:
    knowledge = await db.create_knowledge(knowledge_create=knowledge_create)
    return str(knowledge.id)


# 咱们可以采取一种折衷的方法
# 就是先把知识都添加到一个临时的agent下面
# 类似于linux系统里面的pid=1
# 这样所有的底层数据结构都不需要改
# 否则我们在数据表中把knowledge和agent分开，就用不了sqlalchemy的relationship了，还是挺可惜的
# 也不一定 先试试sql可不可以把


# TODO: 改一下名字，上传文件和上传webpage的接口可以分开
# 毕竟后端处理起来也不一样，前端处理也不一样
@knowledge.post(path="/upload-file")
async def knowledge_upload(
    # bot_id: Annotated[str, Form(description="bot id")],
    knowledge_id: Annotated[UUID, Form(description="knowledge id")],
    file: Annotated[UploadFile, File(description="knowledge file")],
    db: Annotated[Database, Depends(get_db)],
    background_tasks: BackgroundTasks,
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
    # create_knowledge(knowledge_id=knowledge_id, filename=filename)
    # return knowledge_id
    knowledge_point = await db.create_knowledge_point(
        knowledge_point_create=KnowledgePointCreate(
            knowledge_id=knowledge_id,
            path_or_url=filename,
            # category=KnowledgePointCategory.PDF,
        )
    )
    # TODO
    # 讲道理，写成background不好测试
    # 先不用了吧 都测好了再改成backgrou的task
    # background_tasks.add_task(
    #     # 我们真正做的是生成知识库 其实就是学习知识的过程
    #     # 这个过程在langchain里面叫啥来着
    #     # split load, then retrieval
    #     # https://python.langchain.com/v0.2/docs/tutorials/rag/#indexing
    #     # 叫做indexing
    #     func=create_knowledge_indexing,
    #     knowledge_point=knowledge_point,
    # )
    await create_knowledge_indexing(knowledge_point=knowledge_point)
    return str(knowledge_point.id)


@knowledge.post("/upload-url")
async def knowledge_upload_webpage(
    # bot_id: Annotated[str, Form(description="bot id")],
    knowledge_id: Annotated[UUID, Body(description="knowledge id")],
    url: Annotated[str, Body(description="webpage url")],
    # topic: Annotated[str, Form(description="knowledge topic")],
    # 不对，我们在这里使用这个东西是不对的
    # 因为在前端上传链接和文件是不一样的
    # 所以调用的时候肯定不一样
    # 所以这里可以指定一个url 而传文件只能通过form
    # 所以这个是不可能通用的
    # knowledge_point_create: KnowledgePointCreate,
    background_tasks: BackgroundTasks,
    db: Annotated[Database, Depends(get_db)],
) -> str:
    # knowledge_id = str(uuid.uuid4())

    knowledge_point = await db.create_knowledge_point(
        knowledge_point_create=KnowledgePointCreate(
            knowledge_id=knowledge_id,
            path_or_url=url,
            # category=KnowledgePointCategory.WEB_PAGE,
        )
    )
    # background_tasks.add_task(
    #     # 我们真正做的是生成知识库 其实就是学习知识的过程
    #     # 这个过程在langchain里面叫啥来着
    #     # split load, then retrieval
    #     # https://python.langchain.com/v0.2/docs/tutorials/rag/#indexing
    #     # 叫做indexing
    #     func=create_knowledge_indexing,
    #     knowledge_point=knowledge_point,
    # )
    await create_knowledge_indexing(knowledge_point=knowledge_point)
    # 在数据库中添加相关词条
    return str(knowledge_point.id)


# @knowledge.get("/list")
# async def knowledge_list() -> list[str]:
#     return os.listdir(conf.knowledge_file_base_dir)
