# 2024/6/17
# zhangzhong

from app.aibot.agent import Agent
from app.model import ChatMessage


async def test_agent():
    agent = Agent(prompt="Hello, World!", tools=[])
    async for response in agent.ainvoke(
        input=ChatMessage(
            sender=1, receiver=2, is_end_of_stream=True, content="Hello, World!"
        )
    ):
        print(response)
