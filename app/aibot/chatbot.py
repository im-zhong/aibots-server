# 2024/5/8
# zhangzhong

from typing import AsyncGenerator

from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI

from app.common.conf import conf
from app.model.chat import ChatMessage
from app.storage.schema import MessageSchema

from .interface import AIBot


class ChatBot(AIBot):

    def __init__(self, chat_id: str, cid: int, chat_history: list[MessageSchema]):

        self.session_id = str(chat_id)
        self.chat_history: list[MessageSchema] = chat_history
        self.chat_model = ChatOpenAI(
            api_key=conf.openai_api_key,  # type: ignore
            base_url=conf.openai_api_base_url,
        )

        self.store: dict[str, BaseChatMessageHistory] = {}

        prompt = ChatPromptTemplate.from_messages(
            messages=[
                #         (
                #             "system",
                #             """Given a chat history and the latest user question \
                # which might reference context in the chat history, formulate a standalone question \
                # which can be understood without the chat history. Do NOT answer the question, \
                # just reformulate it if needed and otherwise return it as is.""",
                #         ),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
            ]
        )

        chain_without_history = prompt | self.chat_model | StrOutputParser()

        def get_session_history(session_id: str) -> BaseChatMessageHistory:
            if session_id not in self.store:
                self.store[session_id] = ChatMessageHistory()
            return self.store[session_id]

        self.chain = RunnableWithMessageHistory(
            runnable=chain_without_history,
            get_session_history=get_session_history,
            input_messages_key="input",
            history_messages_key="chat_history",
        )

    async def ainvoke(self, input: ChatMessage) -> AsyncGenerator[ChatMessage, None]:
        # self.chat_history.append(MessageSchema(role="user", content=input.content))

        yield ChatMessage(
            sender=1,
            receiver=2,
            is_start_of_stream=True,
            content="Hello, World!",
        )

        # just create a chat model and call it
        async for message in self.chain.astream(
            input={"input": input.content},
            config={"configurable": {"session_id": self.session_id}},
        ):
            pass
            # print(message)
            # response_content = message.content
            yield ChatMessage(
                sender=1,
                receiver=2,
                content=message,
            )

        yield ChatMessage(
            sender=input.receiver,
            receiver=input.sender,
            is_end_of_stream=True,
            content="",
        )
