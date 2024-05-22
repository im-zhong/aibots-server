# 2024/5/8
# zhangzhong
# AIBotFactory

from app.model.chat import AIBotCategory
from app.storage.schema import MessageSchema

# from .rag import RAG
from .chatbot import ChatBot

# from .character import RolePlayer
from .interface import AIBot

# from .reporter import Reporter
# from .retriever import RAG


class AIBotFactory:

    def __init__(
        self,
        # chat_id: int,
        # uid: int,
        # cid: int,
        # category: str,
        # name: str,
        # description: str,
        # knowledge_id: str,
        chat_history: list[MessageSchema] = [],
    ):
        self.category = AIBotCategory.CHAT_BOT
        pass
        # self.chat_id = chat_id
        # self.uid = uid
        # self.cid = cid
        # # rag = Retrieval Augmented Generation
        # if category == "doc_rag":
        #     self.category = AIBotCategory.DOC_RAG
        # elif category == "web_rag":
        #     self.category = AIBotCategory.WEB_RAG
        # elif category == "reporter":
        #     self.category = AIBotCategory.REPORTER
        # elif category == "painter":
        #     self.category = AIBotCategory.PAINTER
        # else:
        #     self.category: AIBotCategory = AIBotCategory.ROLE_PLAYER
        # self.name = name
        # self.description = description
        # self.chat_history = chat_history
        # self.knowledge_id = knowledge_id

    def new(self) -> AIBot:
        pass
        match self.category:
            # case AIBotCategory.REPORTER:
            #     return Reporter(uid=self.uid)
            # case AIBotCategory.DOC_RAG:
            #     return RAG(
            #         cid=self.cid,
            #         uid=self.uid,
            #         chat_id=self.chat_id,
            #         knowledge_id=self.knowledge_id,
            #         chat_history=self.chat_history,
            #     )
            case AIBotCategory.CHAT_BOT:
                return ChatBot(chat_id="test-chat-id", cid=1, chat_history=[])
            case _:
                assert False, f"Unknown category: {self.category}"
