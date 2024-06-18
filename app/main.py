import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.common.conf import conf
from app.router.auth import auth
from app.router.bot import bot
from app.router.chat import chat
from app.router.knowledge import knowledge
from app.storage.database import init_db


# https://fastapi.tiangolo.com/advanced/events/
@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs(conf.knowledge_file_base_dir, exist_ok=True)
    await init_db()
    yield


app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router=auth)
app.include_router(router=chat)
app.include_router(router=knowledge)
app.include_router(router=bot)


@app.get("/")
def read_root():
    return {"Hello": "World"}


# uvicorn app.main:app --reload
# if __name__ == "__main__":
#     uvicorn.run(app, reload=True)
