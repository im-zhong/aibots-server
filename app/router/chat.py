# 2024/4/7
# zhangzhong

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Body, Depends, WebSocket
from langchain.tools import BaseTool

from app.aibot import AIBotFactory
from app.aibot.agent import Agent
from app.aibot.chatbot import ChatBot
from app.model import ChatCreate, ChatMessage, ChatOut, MessageCreate, MessageSender
from app.router.dependency import (
    get_current_user,
    get_db,
    get_user_from_token,
    get_user_manager,
)

# from app.dependency import get_db, get_token_data, get_user
from app.storage.database import Database
from app.storage.schema import AgentSchema, ChatSchema, MessageSchema, UserSchema
from app.tool import RetrieverToolFactory, dalle_tool, search_tool

chat = APIRouter(tags=["chat"])


# https://devcenter.heroku.com/articles/websocket-security#wss


@chat.post(path="/api/chat/create")
async def create_chat(
    chat_create: ChatCreate,
    db: Database = Depends(get_db),
    user: UserSchema = Depends(dependency=get_current_user),
) -> str:
    chat = await db.create_chat(chat_create=chat_create)
    return str(chat.id)


async def create_tools_from_bot(bot: AgentSchema, db: Database) -> list[BaseTool]:
    # 2. second, according to the bot, instance an agent
    tools = []
    if bot.web_search:
        tools.append(search_tool)
    if bot.painting:
        tools.append(dalle_tool)
    # 3. last, according to the knowledge, instance retrieval
    # at this point, we do not have knowledges ever
    # so get the knowledges from database instead

    # for knowledge in await bot.awaitable_attrs.knowledges:
    for knowledge in await db.get_knowledges_of_agent(agent_id=bot.id):
        # every knowledge have an id
        # we should instance a retriever only from this knowledge id
        retrieval_tool = RetrieverToolFactory(knowledge=knowledge).new()
        tools.append(retrieval_tool)
    return tools


@chat.get(path="/api/chat/list")
async def list_chats(
    limit: int,
    db: Database = Depends(get_db),
    user: UserSchema = Depends(dependency=get_current_user),
) -> list[ChatOut]:
    return await db.get_chats(user_id=user.id, limit=limit)  # type: ignore


@chat.get(path="/api/chat/{id}")
async def get_chat(
    id: UUID,
    db: Database = Depends(dependency=get_db),
    user: UserSchema = Depends(dependency=get_current_user),
) -> ChatOut:
    chat: ChatSchema = await db.get_chat_else_throw(chat_id=id)
    if user.id != chat.user_id:
        raise ValueError("You are not the owner of this chat")

    return ChatOut(
        id=chat.id,
        agent_id=chat.agent_id,
        user_id=chat.user_id,
        create_at=chat.create_at,
        chat_history=await chat.awaitable_attrs.messages,
    )


# # https://github.com/fastapi-users/fastapi-users/issues/295
# # ref to that
# async def get_user_from_cookie(
#     websocket: WebSocket, user_manager=Depends(dependency=get_user_manager)
# ):
#     cookie = websocket.cookies.get("fastapiusersauth")
#     user = await cookie_auth_backend.get_strategy().read_token(cookie, user_manager)
#     if not user or not user.is_active:
#         raise WebSocketException("Invalid user")
#     yield user


# 不论如何，我们都可以先创建一个chat
# 拿到他的chatid
# 然后再调用本聊天接口 传入chatid
# 这样就不用区分这个聊天是不是有聊天记录了
# 就只需要写一个接口了
@chat.websocket(path="/ws/chat")
async def websocket_endpoint(
    # db: Annotated[DatabaseService, Depends(get_db)],
    websocket: WebSocket,
    token: str,
    # cid: int,
    # token: str,
    # chat_id: int | None = None,
    chat_id: str,
    db: Database = Depends(get_db),
    # user: UserSchema = Depends(dependency=get_current_user),
    user: UserSchema = Depends(dependency=get_user_from_token),
):
    # token_data = await get_token_data(token=token)
    # user = get_user(token_data=token_data, db=db)

    # how to authenticate the token and get user?
    print(user.id, user.name)

    try:
        await websocket.accept()

        # 首先访问数据库
        chat: ChatSchema = await db.get_chat_else_throw(chat_id=UUID(chat_id))
        print("chat_id", chat.id)

        # instance an agent from this chat
        # 1. first, get the bot from this chat
        bot = await db.get_agent_else_throw(agent_id=chat.agent_id)
        print("agent_id", bot.id)

        # character = db.get_character(cid=cid)
        # chat_history: list[MessageSchema] = []
        # if chat_id is not None:
        #     chat = db.get_chat(chat_id=chat_id)
        #     chat_history = chat.messages
        # else:
        #     chat = db.create_chat(chat_create=model.ChatCreate(uid=user.uid, cid=cid))
        #     chat_id = chat.chat_id

        # aibot = AIBotFactory(
        #     # chat_id=chat_id,
        #     # uid=user.uid,
        #     # cid=character.cid,
        #     # name=character.name,
        #     # category=character.category,
        #     # description=character.description,
        #     # chat_history=chat_history,
        #     # knowledge_id=character.knowledge_id,
        # ).new()

        # 从chat数据库中引入聊天记录
        # 同时在聊天的时候，将聊天记录继续加入到数据库中
        aibot = Agent(
            prompt=bot.prompt,
            # https://docs.sqlalchemy.org/en/20/errors.html#error-xd2s
            # https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html#preventing-implicit-io-when-using-asyncsession
            tools=await create_tools_from_bot(bot=bot, db=db),
            messages=await chat.awaitable_attrs.messages,
        )
        print("create aibot success!")

        # 图片使用base64编码保存可以极大的简化代码，太棒了

        while True:
            print("start waiting for user input...")
            user_input = await websocket.receive_json()
            user_input = ChatMessage(**user_input)
            print(f"user: {user_input.content}")
            content = ""
            async for ai_output in aibot.ainvoke(input=user_input):
                await websocket.send_json(data=ai_output.model_dump())
                content += ai_output.content

            print(f"bot: {content}")
            await db.create_message(
                create=MessageCreate(
                    chat_id=chat.id,
                    content=user_input.content,
                    sender=MessageSender.HUMAN,
                )
            )
            await db.create_message(
                create=MessageCreate(
                    chat_id=chat.id,
                    content=content,
                    sender=MessageSender.AI,
                )
            )

    except Exception as e:
        print(e)
        print("close websocket")
        # if websocket.closed
        await websocket.close()


# @chat.get("/api/chat/select")
# async def select_chat(
#     user: Annotated[schema.User, Depends(get_user)],
#     chat_id: int | None = None,
#     cid: int | None = None,
# ) -> list[model.ChatOut]:
#     chats: list[schema.Chat] = []
#     for chat in user.chats:
#         if chat_id and chat.chat_id != chat_id:
#             continue
#         if cid and chat.cid != cid:
#             continue
#         if chat.is_deleted:
#             continue
#         chats.append(chat)

#     chat_outs: list[model.ChatOut] = []
#     for chat in chats:
#         chat_outs.append(
#             model.ChatOut(
#                 chat_id=chat.chat_id,
#                 uid=chat.uid,
#                 cid=chat.cid,
#                 create_at=chat.create_at,
#                 history=[
#                     model.MessageOut(
#                         content=message.content,
#                         sender=message.sender,
#                         created_at=message.created_at,
#                     )
#                     for message in chat.messages
#                 ],
#             )
#         )

#     return chat_outs


# @chat.post("/api/chat/delete")
# async def delete_chat(
#     chat_ids: Annotated[
#         list[int], Body(description="聊天id列表", examples=[[1, 2, 3]])
#     ],
#     db: Annotated[DatabaseService, Depends(get_db)],
#     user: Annotated[schema.User, Depends(get_user)],
# ):
#     for chat_id in chat_ids:
#         db.delete_chat(chat_id=chat_id)
