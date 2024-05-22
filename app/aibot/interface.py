# 2024/5/22
# zhangzhong
# AIBot interface

from abc import ABC, abstractmethod
from typing import AsyncGenerator

from app.model.chat import ChatMessage


class AIBot(ABC):
    @abstractmethod
    async def ainvoke(self, input: ChatMessage) -> AsyncGenerator[ChatMessage, None]:
        yield ChatMessage(
            sender=1, receiver=2, is_end_of_stream=True, content="Hello, World!"
        )
