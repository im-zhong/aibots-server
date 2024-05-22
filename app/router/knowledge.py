# 2024/5/22
# zhangzhong

from fastapi import APIRouter

knowledge = APIRouter(prefix="/api/knowledge", tags=["knowledge"])


@knowledge.get("/list")
async def knowledge_list():
    return {"knowledge": "list"}


@knowledge.post("/upload")
async def knowledge_upload():
    return {"knowledge": "upload"}
