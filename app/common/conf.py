# 2024/5/13
# zhangzhong

import os
import tomllib
from typing import Any

from pydantic import BaseModel, Field


class FastAPIConf(BaseModel):
    host: str = Field(description="主机")
    port: int = Field(description="端口")


class PostgresConf(BaseModel):
    host: str = Field(description="主机")
    port: int = Field(description="端口")
    username: str = Field(description="用户名")
    password: str = Field(description="密码")
    database: str = Field(description="数据库")


class MinioConf(BaseModel):
    endpoint: str = Field(description="对象存储服务的URL")
    access_key: str = Field(description="用户名")
    secret_key: str = Field(description="密码")
    secure: bool = Field(default=False, description="true代表使用HTTPS")
    bucket_name: str = Field(description="存储桶名称")


class SMTPConf(BaseModel):
    server: str = Field(description="SMTP服务器")
    port: int = Field(description="端口")
    email: str = Field(description="发件人邮箱")
    password: str = Field(description="邮箱密码")
    user: str = Field(description="用户名")


class QdrantConf(BaseModel):
    host: str
    prefer_grpc: bool
    collection_name: str


class OpenAIConf(BaseModel):
    api_key: str = Field(description="openai API Key")
    base_url: str = Field(description="openai API Base URL")


class Conf:
    @staticmethod
    def from_file(file: str) -> "Conf":
        with open(file=file, mode="rb") as f:
            return Conf(tomllib.load(f))

    def __init__(self, conf: dict[str, Any]):
        self.check_conf(conf=conf)
        self._fastapi = FastAPIConf(**conf["fastapi"])
        self._postgres = PostgresConf(**conf["postgres"])
        self._minio = MinioConf(**conf["minio"])
        self._smtp = SMTPConf(**conf["smtp"])
        self._qdrant = QdrantConf(**conf["qdrant"])
        self._openai = OpenAIConf(**conf["openai"])

    def check_conf(self, conf: dict[str, Any]) -> None:
        keys: list[str] = ["fastapi", "postgres", "minio", "smtp"]
        for key in keys:
            if key not in conf:
                raise Exception(f"配置文件中缺少{key}字段")

    @property
    def fastapi_host(self) -> str:
        return self._fastapi.host

    @property
    def fastapi_port(self) -> int:
        return self._fastapi.port

    @property
    def postgres_url(self) -> str:
        # TODO:
        # use async db
        # engine = create_engine('postgresql+asyncpg://user:password@host:port/name')
        return f"postgresql+asyncpg://{self._postgres.username}:{self._postgres.password}@{self._postgres.host}/{conf._postgres.database}"

    @property
    def minio_setting(self):
        d = self._minio.model_dump()
        d.pop("bucket_name")
        return d

    @property
    def minio_bucket_name(self):
        return self._minio.bucket_name

    @property
    def minio_endpoint(self):
        return self._minio.endpoint

    @property
    def save_image_path(self):
        return os.path.join("deploy", "image")

    @property
    def max_file_length(self) -> int:
        return 50 * 1024

    @property
    def knowledge_file_base_dir(self) -> str:
        return "deploy/knowledge"

    @property
    def redis_url(self) -> str:
        return "redis://localhost:6379"

    @property
    def smtp_server(self) -> str:
        return self._smtp.server

    @property
    def smtp_port(self) -> int:
        return self._smtp.port

    @property
    def smtp_user(self) -> str:
        return self._smtp.user

    @property
    def smtp_email(self) -> str:
        return self._smtp.email

    @property
    def smtp_password(self) -> str:
        return self._smtp.password

    @property
    def qdrant_host(self) -> str:
        return self._qdrant.host

    @property
    def qdrant_url(self) -> str:
        return f"http://{self._qdrant.host}"

    @property
    def qdrant_prefer_grpc(self) -> bool:
        return self._qdrant.prefer_grpc

    @property
    def qdrant_collection_name(self) -> str:
        return self._qdrant.collection_name

    @property
    def openai_api_key(self) -> str:
        return self._openai.api_key

    @property
    def openai_api_base_url(self) -> str:
        return self._openai.base_url


conf = Conf.from_file(file="conf.toml")
