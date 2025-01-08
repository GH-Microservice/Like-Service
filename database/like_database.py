from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, declared_attr, sessionmaker
from core.config.config import db_settings

DATABASE_URL = f"postgresql+asyncpg://{db_settings.username}:{db_settings.password.get_secret_value()}@{db_settings.host}:{db_settings.port}/LikeGDB"

like_engine = create_async_engine(DATABASE_URL)

async_session = sessionmaker(bind=like_engine, class_=AsyncSession)


class LikeBase(DeclarativeBase):
    __abstract__ = True
    pass


