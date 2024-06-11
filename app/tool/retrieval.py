# 2024/6/11
# zhangzhong

# 不对啊，咱们所有的机器人都是agent
# retrieval只是一个tool而已
# from app.aibot.rag import RAG

# 只不过retrieval工具的创建需要一个额外的参数
# 不像web search和painting 使用一个单例就行了
from langchain.tools.retriever import create_retriever_tool
from langchain_core.retrievers import BaseRetriever


class RetrieverToolFactory:
    def __init__(self, retriever: BaseRetriever):
        self.retriever = retriever

    def create(self):
        return create_retriever_tool(
            retriever=self.retriever,
            name="langsmith_search",
            description="Search for information about LangSmith. For any questions about LangSmith, you must use this tool!",
        )
