# 2024/5/22
# zhangzhong
import os
import uuid
from typing import Annotated

import aiofiles
from fastapi import APIRouter, Body, Depends, File, Form, HTTPException, UploadFile

from app.common.conf import conf

knowledge = APIRouter(prefix="/api/knowledge", tags=["knowledge"])


# write a api for upload file


@knowledge.post("/upload")
async def knowledge_upload(
    file: Annotated[UploadFile, File(description="knowledge file")],
) -> str:
    knowledge_id = str(uuid.uuid4())
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
    return knowledge_id


@knowledge.get("/list")
async def knowledge_list() -> list[str]:
    return os.listdir(conf.knowledge_file_base_dir)
