# 2024/5/23
# zhangzhong

from fastapi import APIRouter, Depends

from app.model.database import BotCreate, BotOut
from app.router.dependency import get_db
from app.storage.database import DatabaseService

bot = APIRouter(prefix="/api/bot", tags=["bot"])


@bot.post("/create")
async def create_bot(
    bot_create: BotCreate,
    db: DatabaseService = Depends(get_db),
) -> BotOut:
    bot = await db.create_bot(bot_create=bot_create)
    return bot
