# 2024/5/13
# zhangzhong

from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel


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


class ChatOut(BaseModel):
    id: UUID
    user_id: UUID
    agent_id: UUID
    # TODO: correct create_at to created_at
    create_at: datetime

    class Config:
        from_attributes = True
