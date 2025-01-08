from redis.asyncio import StrictRedis
from core.config.config import rmq_settings, redis_settings
from sqlalchemy.ext.asyncio import AsyncSession
from database.like_database import async_session
import aio_pika



async def get_rmq_connection():
    connection = await aio_pika.connect_robust(
        f"amqp://{rmq_settings.rmq_username}:{rmq_settings.rmq_password.get_secret_value()}@{rmq_settings.rmq_host}:{rmq_settings.rmq_port}/"
    )
    try:
        yield connection
    finally:
        await connection.close()


async def get_redis_cli():
    return await StrictRedis(host=redis_settings.host, port=redis_settings.port)


async def get_like_sesison() -> AsyncSession:
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
