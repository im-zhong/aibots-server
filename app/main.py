from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from app.router.auth import auth
from app.storage.database import init_db


# https://fastapi.tiangolo.com/advanced/events/
@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(router=auth)


@app.get("/")
def read_root():
    return {"Hello": "World"}


if __name__ == "__main__":
    uvicorn.run(app)
