# 2024/5/23
# zhangzhong

from fastapi import APIRouter, Depends

from app.model import AgentCreate, AgentOut
from app.router.dependency import get_db
from app.storage.database import Database
from app.storage.schema import AgentSchema
from app.model import AddKnowledges

agent = APIRouter(prefix="/api/agent", tags=["agent"])

# TODO: rewrite agent routers, agent和knowledge解耦
# 可能底层的表也要重构一下？


@agent.post(path="/create")
async def create_agent(
    agent_create: AgentCreate,
    db: Database = Depends(get_db),
) -> AgentOut:
    agent: AgentSchema = await db.create_agent(agent_create=agent_create)
    return agent  # type: ignore


@agent.post(path="/add-knowledges")
async def add_knowledges(
    request: AddKnowledges,
    db: Database = Depends(get_db),
) -> None:
    await db.add_knowledges_to_agent(
        agent_id=request.agent_id, knowledge_ids=request.knowledge_ids
    )
