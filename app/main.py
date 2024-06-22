import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.common.conf import conf
from app.router import auth, bot, chat, knowledge, user
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
    # 最开始写成这样，后面多了一个 /
    # 就会报CORS错误。。。这么严格的吗
    "http://172.23.252.251:3000",
]

# cookie有点麻烦啊
# 而且怎么那么多安全隐患呢？
# 感觉不如jwt呀
# 而且我们后续使用chat功能的时候，也需要验证啊
# 但是我们又没有办法使用cookie 因为websocket不支持http header       #
# 感觉真不如jwt。。。
# SameSite=Strict will prevent the cookie from being sent on any cross-site requests.
# SameSite=Lax allows the cookie to be sent with top-level navigations that are considered "safe" (GET requests), but it will not be sent with API requests made using methods such as POST, PUT, DELETE, etc., from a different site.
# SameSite=None explicitly allows the cookie to be sent with cross-site requests. However, when SameSite=None is used, the Secure attribute must also be set, meaning the cookie will only be sent over secure (HTTPS) connections.
# 根据这个说法，我们必须使用https + samesite=none才能正常使用cookie调API
# 所以显然不合适啊
# 果然还是jwt适合API
# 改！TODO
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router=auth)
app.include_router(router=user)
app.include_router(router=chat)
app.include_router(router=knowledge)
app.include_router(router=bot)


@app.get("/")
def read_root():
    return {"Hello": "World"}


# uvicorn app.main:app --reload
# if __name__ == "__main__":
#     uvicorn.run(app, reload=True)
