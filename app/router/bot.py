# 2024/5/23
# zhangzhong

from fastapi import APIRouter, Depends

from app.model import AgentCreate, AgentOut
from app.router.dependency import get_db
from app.storage.database import Database

bot = APIRouter(prefix="/api/agent", tags=["bot"])

# TODO: rewrite agent routers, agent和knowledge解耦
# 可能底层的表也要重构一下？


@bot.post("/create")
async def create_bot(
    bot_create: AgentCreate,
    db: Database = Depends(get_db),
) -> AgentOut:
    bot = await db.create_agent(agent_create=bot_create)
    return bot
