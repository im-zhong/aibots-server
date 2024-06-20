# 2024/5/9
# zhangzhong
# https://python.langchain.com/v0.1/docs/modules/data_connection/vectorstores/#asynchronous-operations
# https://api.python.langchain.com/en/latest/vectorstores/langchain_community.vectorstores.qdrant.Qdrant.html

import uuid

from langchain_community.document_loaders import (
    PDFMinerLoader,
    TextLoader,
    WebBaseLoader,
)
from langchain_community.document_loaders.base import BaseLoader
from langchain_community.vectorstores.qdrant import Qdrant
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_text_splitters import RecursiveCharacterTextSplitter

# https://python-client.qdrant.tech/
from qdrant_client import AsyncQdrantClient, QdrantClient

from app.common import conf
from app.llm import embedding
from app.storage.schema import KnowledgePointSchema

# 所以embedding并没有添加到langchain里面
# langchain_community.embeddings 里面确实没有ZhipuAI的embedding

# https://python.langchain.com/docs/integrations/vectorstores/qdrant/


class LoaderFactory:
    def __init__(self, file_or_url: str):
        self.file_or_url = file_or_url

    def new(self) -> BaseLoader:
        # TODO
        # 突然也感觉到不太对，有很多文件的后缀都不是txt
        # 但是应该作为文本文件
        # 如各种代码的源文件 各种配置文件等等
        # 后缀太多了 没法一一列出来
        if self.file_or_url.startswith("http"):
            return WebBaseLoader(web_path=self.file_or_url)
        elif self.file_or_url.endswith(("txt", "py")):
            return TextLoader(file_path=self.file_or_url)
        elif self.file_or_url.endswith("pdf"):
            return PDFMinerLoader(file_path=self.file_or_url)
        else:
            raise ValueError(f"Unsupported file type: {self.file_or_url}")
        # if self.file.endswith("txt"):
        #     return TextLoader(file_path=self.file)
        # elif self.file.endswith("pdf"):
        #     return PDFMinerLoader(file_path=self.file)
        # else:
        #     raise ValueError(f"Unsupported file type: {self.file}")


# class KnowledgeBase:
#     async def __init__(self, urls: list[str] = [], files: list[str] = []):
#         documents: list[Document] = []
#         for url in urls:
#             documents.extend(WebBaseLoader(web_path=url).load())
#         for file in files:
#             documents.extend(LoaderFactory(file=file).new().load())

#         splitter = RecursiveCharacterTextSplitter(
#             chunk_size=1000, chunk_overlap=200, add_start_index=True
#         )
#         documents = splitter.split_documents(documents=documents)

#         # add metadata for multi tenancy
#         self.knowledge_id = str(uuid.uuid4())
#         for doc in documents:
#             doc.metadata["knowledge_id"] = self.knowledge_id

#         # langchain的异步并不是用async实现的 而是用thread实现的
#         # 所以我们反而不能用异步client
#         client = QdrantClient(
#             url=conf.qdrant_host,
#             prefer_grpc=conf.qdrant_prefer_grpc,
#             collection_name=conf.qdrant_collection_name,
#         )
#         collection_name = "MyCollection"
#         qdrant = Qdrant(client, collection_name, embedding_function)

#         self.collection_name = "my_documents"
#         await qdrant.aadd_documents(
#             documents=documents,
#             embedding=embedding,
#             url=conf.qdrant_host,
#             prefer_grpc=conf.qdrant_prefer_grpc,
#             collection_name=conf.qdrant_collection_name,
#         )

#         qdrant.as_retriever(
#             search_kwargs={"filter": {"knowledge_id": self.knowledge_id}}
#         )

#     @staticmethod
#     def as_retriever(knowledge_id: str):
#         vector_store = Qdrant.from_documents(
#             documents=[Document(page_content="hello")],
#             embedding=embedding,
#             url=conf.qdrant_host,
#             prefer_grpc=conf.qdrant_prefer_grpc,
#             collection_name=conf.qdrant_collection_name,
#         )
#         return vector_store.as_retriever(
#             search_kwargs={"filter": {"knowledge_id": knowledge_id}}
#         )

#     def get_knowledge_id(self) -> str:
#         return self.knowledge_id


# 那么这个client其实也只需要一个就ok了
class VectorStore:
    def __init__(self):

        # let langchain create this collection for us
        Qdrant.from_documents(
            documents=[Document(page_content="hello")],
            embedding=embedding,
            url=conf.qdrant_host,
            prefer_grpc=conf.qdrant_prefer_grpc,
            collection_name=conf.qdrant_collection_name,
        )

        # https://qdrant.tech/documentation/frameworks/langchain/
        # https://python-client.qdrant.tech/qdrant_client.qdrant_client
        self.client = QdrantClient(url=conf.qdrant_url)
        self.async_client = AsyncQdrantClient(
            url=conf.qdrant_host,
            # 感觉这个prefer grpc也没必要，如无必要 勿增实体
            # prefer_grpc=conf.qdrant_prefer_grpc,
            # collection_name无法在一开始指定好像
            # collection_name=conf.qdrant_collection_name,
        )

        self.qdrant = Qdrant(
            client=self.client,
            async_client=self.async_client,
            collection_name=conf.qdrant_collection_name,
            embeddings=embedding,
        )

        collection_info = self.client.get_collection(
            collection_name=conf.qdrant_collection_name
        )
        print(collection_info)

        # if the collection is not exist, we should create it first
        # let's check how langchain create it

    async def add_knowledge_point(self, knowledge_id: str, file_or_url: str):
        loader = LoaderFactory(file_or_url=file_or_url).new()
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200, add_start_index=True
        )

        documents = splitter.split_documents(documents=loader.load())
        for doc in documents:
            doc.metadata["knowledge_id"] = knowledge_id

        await self.qdrant.aadd_documents(documents=documents)

    def get_retriever(self, knowledge_id: str) -> VectorStoreRetriever:
        return self.qdrant.as_retriever(
            search_kwargs={"filter": {"knowledge_id": knowledge_id}}
        )


vector_store = VectorStore()
