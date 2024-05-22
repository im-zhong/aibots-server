from pydantic import BaseModel


class ChatMessage(BaseModel):
    # chat_id: int
    sender: int
    receiver: int
    is_end_of_stream: bool
    content: str
    images: list[str] = []
