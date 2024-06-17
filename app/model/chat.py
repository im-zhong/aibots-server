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
    user_id: UUID
    bot_id: UUID


class MessageSender(str, Enum):
    HUMAN = "human"
    AI = "ai"
    SYSTEM = "system"
