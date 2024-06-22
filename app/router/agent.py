# 2024/5/23
# zhangzhong

from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, Depends

from app.model import AddKnowledges, AgentCreate, AgentOut
from app.router.dependency import get_current_user, get_db
from app.storage.database import Database
from app.storage.schema import AgentSchema, UserSchema

agent = APIRouter(prefix="/api/agent", tags=["agent"])

# TODO:DONE rewrite agent routers, agent和knowledge解耦
# 可能底层的表也要重构一下？

# TODO: 给所有接口添加权限验证


@agent.post(path="/create")
async def create_agent(
    agent_create: AgentCreate,
    # 我大概知道是为什么
    # 因为db打开了一个async session
    # 但是get current user又打开了一个session
    db: Database = Depends(dependency=get_db),
    user: UserSchema = Depends(dependency=get_current_user),
    # user: UserSchema = Depends(fastapi_users.current_user(active=True, verified=True)),
) -> AgentOut:
    agent: AgentSchema = await db.create_agent(agent_create=agent_create)
    return agent  # type: ignore
    # 为什么这俩会公用一个session？
    # 还是sql限制了每个线程只能有一个session？

    # return AgentOut(
    #     **agent_create.model_dump(),
    #     id=uuid4(),
    #     # user_id=user.id,
    #     created_at=datetime.now()
    # )


@agent.post(path="/add-knowledges")
async def add_knowledges(
    request: AddKnowledges,
    db: Database = Depends(dependency=get_db),
    user: UserSchema = Depends(dependency=get_current_user),
) -> None:
    await db.add_knowledges_to_agent(
        agent_id=request.agent_id, knowledge_ids=request.knowledge_ids
    )


# I need to add a new router to search and list agents
# first, write a very simple api to list all agents, only for tests
@agent.get(path="/list")
async def list_agents(
    limit: int,
    db: Database = Depends(dependency=get_db),
    user: UserSchema = Depends(dependency=get_current_user),
) -> list[AgentOut]:
    return await db.get_agents(user_id=user.id, limit=limit)  # type: ignore
