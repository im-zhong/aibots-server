# 2024/6/12
# zhangzhong

from fastapi import APIRouter, Depends

# from app.model.database import BotCreate, BotOut
from app.router.dependency import get_db
from app.storage.database import Database

# agent = APIRouter(prefix="/api/agent", tags=["agent"])


# @agent.post("/create")
# async def create_agent(
#     bot_create: BotCreate,
#     db: DatabaseService = Depends(get_db),
# ) -> BotOut:
#     bot = await db.create_bot(bot_create=bot_create)
#     return bot
