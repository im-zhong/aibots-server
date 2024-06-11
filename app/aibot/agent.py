# 2024/5/30
# zhangzhong
# https://python.langchain.com/v0.1/docs/use_cases/tool_use/
# https://python.langchain.com/v0.1/docs/modules/tools/
# https://python.langchain.com/v0.1/docs/modules/agents/agent_types/tool_calling/
# https://python.langchain.com/v0.1/docs/modules/memory/agent_with_memory/

from langchain import hub
from langchain.agents import AgentExecutor, create_tool_calling_agent

# 具体要创建什么样的agent，只取决于所使用的工具而已
# 感觉还应该输入一个初始的的prompt就ok啦
from langchain.tools import BaseTool
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

from app.llm import chat_model, embedding


class AgentFactory:
    def __init__(self, prompt: str, tools: list[BaseTool]):
        self.tools = tools
        self.prompt = prompt = hub.pull("hwchase17/openai-functions-agent")

    def create(self):
        # 我发现很多地方都直接使用了openai的模型
        # 我们应该封装一个llm模块，专门提供这些模型
        # 单例 直接用全局变量就ok
        agent = create_tool_calling_agent(
            llm=chat_model, tools=self.tools, prompt=self.prompt
        )

        chat_history = ChatMessageHistory()
        executor = RunnableWithMessageHistory(
            runnable=agent,
            get_session_history=lambda session_id: chat_history,
            input_messages_key="input",
            history_messages_key="chat_history",
            # 这就说明agent executor的返回值就是Message，所以我们才不需要指定output key
            # 或者说，我们就是想把模型的输出一整个作为Message，加入到历史记录中
        )

        return executor
