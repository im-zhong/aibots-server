# 2024/5/22
# zhangzhong

import asyncio

from app.aibot.chatbot import ChatBot
from app.model.chat import ChatMessage

# async def test_chatbot():
#     chatbot = ChatBot(chat_id="chat_id", cid=1, chat_history=[])

#     async for message in chatbot.ainvoke(
#         input=ChatMessage(sender=1, receiver=2, is_end_of_stream=True, content="hello")
#     ):
#         print(message.content, end="")
