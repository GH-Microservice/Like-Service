from fastapi import FastAPI
from apps.like_service.router import like_service_router
from database.like_database import like_engine, LikeBase

app = FastAPI(title="Like Service API")

app.include_router(like_service_router)


async def create_teables():
    async with like_engine.begin() as conn:
        await conn.run_sync(LikeBase.metadata.create_all)


@app.on_event("startup")
async def on_startup():
    return await create_teables()
