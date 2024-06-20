# 2024/5/23
# zhangzhong

from fastapi import APIRouter, Depends

from app.model import BotCreate, BotOut
from app.router.dependency import get_db
from app.storage.database import Database

bot = APIRouter(prefix="/api/agent", tags=["bot"])


@bot.post("/create")
async def create_bot(
    bot_create: BotCreate,
    db: Database = Depends(get_db),
) -> BotOut:
    bot = await db.create_bot(bot_create=bot_create)
    return bot
