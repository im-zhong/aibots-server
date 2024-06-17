# 2024/6/11
# zhangzhong

# 不对啊，咱们所有的机器人都是agent
# retrieval只是一个tool而已
# from app.aibot.rag import RAG

from uuid import UUID

# 只不过retrieval工具的创建需要一个额外的参数
# 不像web search和painting 使用一个单例就行了
from langchain.tools.retriever import create_retriever_tool
from langchain_core.retrievers import BaseRetriever

from app.storage.schema import KnowledgeSchema
from app.storage.vector_store import vector_store


class RetrieverToolFactory:
    # 不如传递一个knowledge进来
    def __init__(self, knowledge: KnowledgeSchema):
        self.knowledge = knowledge
        self.retriever = vector_store.get_retriever(knowledge_id=str(self.knowledge.id))

    def new(self):
        topic = self.knowledge.topic
        return create_retriever_tool(
            retriever=self.retriever,
            name=topic,
            description=f"Search for information about {topic}. For any questions about {topic}, you must use this tool!",
        )
