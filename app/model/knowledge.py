# 2024/6/14
# zhangzhong

from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


class KnowledgePointCategory(str, Enum):
    PDF = "pdf"
    TXT = "txt"
    WEB_PAGE = "web_page"


class KnowledgeCreate(BaseModel):
    bot_id: UUID = Field(description="机器人id")
    topic: str = Field(description="知识库主题")


class KnowledgePointCreate(BaseModel):
    knowledge_id: UUID
    category: KnowledgePointCategory
    path_or_url: str
