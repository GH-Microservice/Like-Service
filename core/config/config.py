from pydantic import BaseModel, SecretStr
from typing import Optional
from dotenv import load_dotenv
import os

load_dotenv()


class DBSettings(BaseModel):
    username: str
    password: SecretStr
    host: str
    port: int


class AuthSettingsScheme(BaseModel):
    secret_key: SecretStr
    algoritm: str
    accsess_token_expire_days: int


class RmqSettingsScheme(BaseModel):
    rmq_username: str
    rmq_password: SecretStr
    rmq_host: str
    rmq_port: int


class RedisSettingsScheme(BaseModel):
    host: str
    port: int


class EmailConfigScheme(BaseModel):
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int = (587,)
    MAIL_SERVER: str = ("smtp.gmail.com",)
    MAIL_STARTTLS: bool = (True,)
    MAIL_SSL_TLS: bool = (False,)
    USE_CREDENTIALS: bool = (True,)
    VALIDATE_CERTS: bool = True


db_settings = DBSettings(
    username=os.getenv("PG_USERNAME"),
    password=os.getenv("PG_PASSWORD"),
    port=os.getenv("PG_PORT"),
    host=os.getenv("PG_HOST"),
)


auth_settings = AuthSettingsScheme(
    secret_key=os.getenv("SECRET_KEY"),
    accsess_token_expire_days=365,
    algoritm="HS256",
)


rmq_settings = RmqSettingsScheme(
    rmq_username=os.getenv("RMQ_USERNAME"),
    rmq_password=os.getenv("RMQ_PASSWORD"),
    rmq_host=os.getenv("RMQ_HOST"),
    rmq_port=os.getenv("RMQ_PORT"),
)


redis_settings = RedisSettingsScheme(host="localhost", port="6379")
