# 2024/5/30
# zhangzhong
# https://python.langchain.com/v0.1/docs/use_cases/tool_use/
# https://python.langchain.com/v0.1/docs/modules/tools/
# https://python.langchain.com/v0.1/docs/modules/agents/agent_types/tool_calling/
# https://python.langchain.com/v0.1/docs/modules/memory/agent_with_memory/
# https://python.langchain.com/v0.1/docs/modules/agents/quick_start/
# https://python.langchain.com/v0.1/docs/modules/agents/concepts/

from typing import AsyncGenerator

from langchain import hub
from langchain.agents import AgentExecutor, create_tool_calling_agent

# 具体要创建什么样的agent，只取决于所使用的工具而已
# 感觉还应该输入一个初始的的prompt就ok啦
from langchain.tools import BaseTool
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from langchain_core.runnables.history import RunnableWithMessageHistory

from app.aibot.interface import AIBot
from app.llm import chat_model, embedding
from app.model import ChatMessage, MessageSender
from app.storage.schema import MessageSchema

# 这个是创建Agent的时候，使用这个东西创建一个Agent
# 这个更需要做的东西是从数据库中拿出来之后，将kid转换成tool，把相应的参数，比如是否开启绘画能力等转换成tool，用户传入的prompt穿进去
# 大概是这样的
# 这个类真的有必要吗？先不写了吧，写到后面真的有用到再说吧
# class AgentFactory:
#     def __init__(self, prompt: str, tools: list[BaseTool] = []):
#         # self.tools = tools
#         # self.prompt = prompt = hub.pull("hwchase17/openai-functions-agent")
#         pass

#     def create(self):
#         # # 我发现很多地方都直接使用了openai的模型
#         # # 我们应该封装一个llm模块，专门提供这些模型
#         # # 单例 直接用全局变量就ok
#         # agent = create_tool_calling_agent(
#         #     llm=chat_model, tools=self.tools, prompt=self.prompt
#         # )

#         # chat_history = ChatMessageHistory()
#         # executor = RunnableWithMessageHistory(
#         #     runnable=agent,
#         #     get_session_history=lambda session_id: chat_history,
#         #     input_messages_key="input",
#         #     history_messages_key="chat_history",
#         #     # 这就说明agent executor的返回值就是Message，所以我们才不需要指定output key
#         #     # 或者说，我们就是想把模型的输出一整个作为Message，加入到历史记录中
#         # )

#         return executor


# 这个是聊天的时候，创建一个具体的Agent的实例
class Agent(AIBot):
    def __init__(
        self,
        prompt: str = "",
        tools: list[BaseTool] = [],
        messages: list[MessageSchema] = [],
    ):
        # self.executor = AgentFactory(prompt, tools).create()
        self.prompt = hub.pull("hwchase17/openai-functions-agent")
        # agent = create_tool_calling_agent(
        #     llm=chat_model, tools=tools, prompt=self.prompt
        # )
        self.chat_history = Agent.create_chat_history_from_messages(messages=messages)
        agent_executor = AgentExecutor(
            agent=create_tool_calling_agent(
                llm=chat_model, tools=tools, prompt=self.prompt
            ),
            tools=tools,
            verbose=True,
            stream_runnable=False,  # type: ignore
        )
        self.agent = RunnableWithMessageHistory(
            runnable=agent_executor,  # type: ignore
            get_session_history=lambda session_id: self.chat_history,
            input_messages_key="input",
            history_messages_key="chat_history",
            # 这就说明agent executor的返回值就是Message，所以我们才不需要指定output key
            # 或者说，我们就是想把模型的输出一整个作为Message，加入到历史记录中
        )

    @staticmethod
    def create_chat_history_from_messages(messages: list[MessageSchema]):
        chat_history = ChatMessageHistory()
        for message in messages:
            chat_history.add_message(
                message=Agent.create_base_message_from_message_schema(message=message)
            )
        return chat_history

    # 还需要定义一个函数，就是从MessageSchema到BaseMessage
    @staticmethod
    def create_base_message_from_message_schema(message: MessageSchema) -> BaseMessage:
        if message.sender == MessageSender.AI:
            return AIMessage(
                content=message.content,
            )
        elif message.sender == MessageSender.HUMAN:
            return HumanMessage(
                content=message.content,
            )
        elif message.sender == MessageSender.SYSTEM:
            return SystemMessage(
                content=message.content,
            )
        else:
            raise ValueError(f"Unknown sender: {message.sender}")

    async def ainvoke(self, input: ChatMessage) -> AsyncGenerator[ChatMessage, None]:
        response: dict = self.agent.invoke(
            input={"input": input.content},
            config={"configurable": {"session_id": "session"}},
        )
        print(response)
        yield ChatMessage(
            sender=1, receiver=2, is_end_of_stream=True, content=response["output"]
        )
