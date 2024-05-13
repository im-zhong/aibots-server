# 2024/4/8
# zhangzhong
# redefine all the models

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class Role(str, Enum):
    USER = "user"
    ADMIN = "admin"


class UserCreate(BaseModel):
    email: str = Field(description="邮箱")
    name: str = Field(description="用户名")
    password: str = Field(description="密码")
    # 应该来说，是先上传头像，返回头像
    # https://fastapi.tiangolo.com/advanced/custom-response/#fileresponse
    # 我懂了，不管是上传头像还是上传文件
    # 都是先上传完毕之后，后端返回一个id，然后前端再传回这个ID
    # 后端根据这个id找到对应的文件，这样我们就不需要把minio服务或者本地文件系统给暴露出来了
    # avatar_id: str = Field(description="头像id")


class UserUpdate(BaseModel):
    name: str | None = Field(default=None, description="用户名")
    # avatar_id: str | None = Field(default=None, description="头像id")


class UserPasswordUpdate(BaseModel):
    old_password: str = Field(description="旧密码")
    new_password: str = Field(description="新密码")


class UserOut(BaseModel):
    id: int = Field(description="用户id")
    name: str = Field(description="用户名")
    # avatar_id: str = Field(description="头像url")
    # role: str = Field(description="用户角色")
    created_at: datetime = Field(description="创建时间")

    class Config:
        from_attributes = True


class BotCategory(str, Enum):
    CHAT_BOT = "chat_bot"
    RAG = "rag"
    PAINTER = "painter"


# character
class BotCreate(BaseModel):
    name: str = Field(description="机器人名称")
    description: str = Field(description="机器人信息")
    # avatar_description: str | None = Field(default=None, description="头像描述")
    # avatar_url: str = Field(description="头像url")
    category: str = Field(description="机器人类型")
    # 感觉这个东西作为字段名不太好
    user_id: int = Field(description="用户id")
    is_shared: bool = Field(default=False, description="是否共享")
    # 这里需要先上传文件，后端返回id之后，再把id上传
    knowledge_id: str | None = Field(default=None, description="知识库ID")
    # memory_id: str | None = Field(default=None, description="记忆库ID")


# 现在没必要定义这么多模型
# 等前端设计的时候，发现确实需要那些接口，咱们再来写就ok拉
# 因为sqlalchemy的底层实现非常简单
# 所以提供一个where的model非常方便
# class BotWhere(BaseModel):
#     uid: int | None = None
#     cid: int | None = None
#     name: str | None = None
#     category: str | None = None


# class BotUpdate(BaseModel):
#     name: str | None = Field(default=None, description="机器人名称")
#     description: str | None = Field(default=None, description="机器人信息")
#     category: str | None = Field(default=None, description="机器人类型")
#     avatar_description: str | None = Field(default=None, description="头像描述")
#     avatar_url: str | None = Field(default=None, description="头像url")


class BotOut(BaseModel):
    id: int = Field(description="机器人id")
    name: str = Field(description="机器人名称")
    description: str = Field(description="机器人信息")
    category: BotCategory = Field(description="机器人类型")
    # avatar_description: str | None = Field(description="头像描述")
    # avatar_url: str = Field(description="头像url")
    created_at: datetime = Field(description="创建时间")
    # updated_at: datetime | None = Field(description="更新时间")
    # is_deleted: bool = Field(description="是否删除")
    is_shared: bool = Field(description="是否共享")
    user_id: int = Field(description="用户id")

    class Config:
        from_attributes = True


# user or uid
# uid is better, cause we would like the 'user' to indicate the whole object
# so uid , user
# cid, character
# chat_id, chat
# content_id, content
# why not message, so we could use mid


class ChatCreate(BaseModel):
    user_id: int = Field(description="用户id")
    bot_id: int = Field(description="机器人id")


class MessageSender(str, Enum):
    HUMAN = "human"
    AI = "ai"
    SYSTEM = "system"
    TOOL = "tool"


class MessageCreate(BaseModel):
    chat_id: int = Field(description="聊天id")
    content: str = Field(description="聊天内容")
    sender: MessageSender = Field(description="发送者")


class MessageOut(BaseModel):
    content: str
    sender: MessageSender
    created_at: datetime


class ChatOut(BaseModel):
    id: int = Field(description="聊天id")
    user_id: int = Field(description="用户id")
    bot_id: int = Field(description="机器人id")
    create_at: datetime = Field(description="创建时间")
    # 所有的聊天记录也要保证按照时间排序
    history: list[MessageOut]

    class Config:
        from_attributes = True


# class ChatWhere(BaseModel):
#     chat_id: int | None = None
#     cid: int | None = None


class ChatMessage(BaseModel):
    # chat_id: int
    sender: int
    receiver: int
    is_end_of_stream: bool
    content: str
    images: list[str] = []
