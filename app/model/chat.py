# 2024/5/13
# zhangzhong

from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    # chat_id: int
    sender: int
    receiver: int
    is_start_of_stream: bool = False
    is_end_of_stream: bool = False
    content: str
    images: list[str] = []


class ChatCreate(BaseModel):
    user_id: str
    agent_id: str


class MessageSender(str, Enum):
    HUMAN = "human"
    AI = "ai"
    SYSTEM = "system"


class MessageOut(BaseModel):
    id: UUID
    sender: MessageSender
    content: str
    # TODO: correct to list[str]
    images: str = Field(default="")
    created_at: datetime

    class Config:
        from_attributes = True


class ChatOut(BaseModel):
    id: UUID
    user_id: UUID
    agent_id: UUID
    # TODO: correct create_at to created_at
    create_at: datetime
    chat_history: list[MessageOut] = []

    class Config:
        from_attributes = True


class MessageCreate(BaseModel):
    chat_id: UUID
    content: str
    sender: MessageSender
    images: str = Field(default="")
