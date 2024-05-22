from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.router.auth import auth
from app.router.chat import chat
from app.storage.database import init_db


# https://fastapi.tiangolo.com/advanced/events/
@asynccontextmanager
async def lifespan(app: FastAPI):
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


@app.get("/")
def read_root():
    return {"Hello": "World"}


# uvicorn app.main:app --reload
# if __name__ == "__main__":
#     uvicorn.run(app, reload=True)
