# 2024/6/14
# zhangzhong

import uuid
from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


class AIBotCategory(str, Enum):
    ROLE_PLAYER = "role_player"
    DOC_RAG = "doc_rag"
    WEB_RAG = "web_rag"
    REPORTER = "reporter"
    PAINTER = "painter"
    CHAT_BOT = "chat_bot"


class BotCategory(str, Enum):
    CHAT_BOT = "chat_bot"
    RAG = "rag"
    PAINTER = "painter"


class AgentCreate(BaseModel):
    name: str = Field(description="机器人名称")
    user_id: uuid.UUID = Field(description="用户id")
    description: str = Field(description="机器人信息")
    # avatar_description: str | None = Field(default=None, description="头像描述")
    # avatar_url: str = Field(description="头像url")
    # category: str = Field(description="机器人类型")
    # 感觉这个东西作为字段名不太好
    # user_id: int = Field(description="用户id")
    is_shared: bool = Field(default=False, description="是否共享")
    # 这里需要先上传文件，后端返回id之后，再把id上传
    # id是唯一的，文件id是文件id，knowledgeid是知识库id，不冲突
    # 某个角色的知识都在这个kid下面
    # 但是这个id是后端生成的，不是前端传过来的
    # 前端需要传的是文件id
    # knowledge_id: str | None = Field(default=None, description="知识库ID")
    # memory_id: str | None = Field(default=None, description="记忆库ID")
    # knowledges: list[str] = Field(default=[], description="文件ID")
    prompt: str = Field(default="", description="提示")
    web_search: bool = Field(default=False, description="是否开启网络搜索")
    painting: bool = Field(default=False, description="是否开启绘画")
    multi_model: bool = Field(default=False, description="是否开启多模型")


#
# # 现在没必要定义这么多模型
# # 等前端设计的时候，发现确实需要那些接口，咱们再来写就ok拉
# # 因为sqlalchemy的底层实现非常简单
# # 所以提供一个where的model非常方便
# # class BotWhere(BaseModel):
# #     uid: int | None = None
# #     cid: int | None = None
# #     name: str | None = None
# #     category: str | None = None
#
#
# # class BotUpdate(BaseModel):
# #     name: str | None = Field(default=None, description="机器人名称")
# #     description: str | None = Field(default=None, description="机器人信息")
# #     category: str | None = Field(default=None, description="机器人类型")
# #     avatar_description: str | None = Field(default=None, description="头像描述")
# #     avatar_url: str | None = Field(default=None, description="头像url")
#
#
class AgentOut(BaseModel):
    id: uuid.UUID = Field(description="机器人id")
    user_id: uuid.UUID = Field(description="用户id")
    name: str = Field(description="机器人名称")
    avatar: str = Field(default="", description="头像")
    description: str = Field(description="机器人信息")
    # category: BotCategory = Field(description="机器人类型")
    # avatar_description: str | None = Field(description="头像描述")
    # avatar_url: str = Field(description="头像url")
    created_at: datetime = Field(description="创建时间")
    # updated_at: datetime | None = Field(description="更新时间")
    # is_deleted: bool = Field(description="是否删除")
    is_shared: bool = Field(description="是否共享")

    class Config:
        from_attributes = True


class AddKnowledges(BaseModel):
    agent_id: UUID
    knowledge_ids: list[UUID]
