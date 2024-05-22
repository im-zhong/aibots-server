from enum import Enum

from pydantic import BaseModel


class ChatMessage(BaseModel):
    # chat_id: int
    sender: int
    receiver: int
    is_start_of_stream: bool = False
    is_end_of_stream: bool = False
    content: str
    images: list[str] = []


class AIBotCategory(str, Enum):
    ROLE_PLAYER = "role_player"
    DOC_RAG = "doc_rag"
    WEB_RAG = "web_rag"
    REPORTER = "reporter"
    PAINTER = "painter"
    CHAT_BOT = "chat_bot"
