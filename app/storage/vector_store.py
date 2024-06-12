# 2024/5/9
# zhangzhong


import uuid

from langchain_community.document_loaders import (
    PDFMinerLoader,
    TextLoader,
    WebBaseLoader,
)
from langchain_community.document_loaders.base import BaseLoader
from langchain_community.vectorstores.qdrant import Qdrant
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.common import conf

# from app.llm import ZhipuAIEmbeddings

# 所以embedding并没有添加到langchain里面
# langchain_community.embeddings 里面确实没有ZhipuAI的embedding

# https://python.langchain.com/docs/integrations/vectorstores/qdrant/
# 咱们使用OpenAI的embedding，这个embedding是在langchain里面的


embedding = OpenAIEmbeddings(
    api_key=conf.openai_api_key,  # type: ignore
    base_url=conf.openai_api_base_url,
)


class LoaderFactory:
    def __init__(self, file: str):
        self.file = file

    def new(self) -> BaseLoader:
        if self.file.endswith("txt"):
            return TextLoader(file_path=self.file)
        elif self.file.endswith("pdf"):
            return PDFMinerLoader(file_path=self.file)
        else:
            raise ValueError(f"Unsupported file type: {self.file}")


class KnowledgeBase:
    def __init__(self, knowledge_id: str, urls: list[str] = [], files: list[str] = []):
        documents: list[Document] = []
        for url in urls:
            documents.extend(WebBaseLoader(web_path=url).load())
        for file in files:
            documents.extend(LoaderFactory(file=file).new().load())

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200, add_start_index=True
        )
        documents = splitter.split_documents(documents=documents)

        # add metadata for multi tenancy
        self.knowledge_id = knowledge_id
        for doc in documents:
            doc.metadata["knowledge_id"] = self.knowledge_id

        self.collection_name = "my_documents"
        self.vector_store = Qdrant.from_documents(
            documents=documents,
            embedding=embedding,
            url=conf.qdrant_host,
            prefer_grpc=conf.qdrant_prefer_grpc,
            collection_name=conf.qdrant_collection_name,
        )

    @staticmethod
    def as_retriever(knowledge_id: str):
        vector_store = Qdrant.from_documents(
            documents=[Document(page_content="hello")],
            embedding=embedding,
            url=conf.qdrant_host,
            prefer_grpc=conf.qdrant_prefer_grpc,
            collection_name=conf.qdrant_collection_name,
        )
        return vector_store.as_retriever(
            search_kwargs={"filter": {"knowledge_id": knowledge_id}}
        )

    def get_knowledge_id(self) -> str:
        return self.knowledge_id
