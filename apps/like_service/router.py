from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from redis import StrictRedis
from aio_pika import RobustConnection
from core.dependencies.dependencies import get_redis_cli, get_rmq_connection, get_like_sesison
from apps.like_service.service import LikeService, LikeScheme
from utils.utils import get_current_user
from utils.scheme import SUser


like_service_router = APIRouter(tags=["Like Service"], prefix="/like-service/api/v1")


@like_service_router.post("/create-like/{repository_id}/")
async def create_like(repository_id: int, session: AsyncSession = Depends(get_like_sesison), current_user: SUser = Depends(get_current_user)):
    service = LikeService(session=session, current_user = current_user)
    return await service._create_like(repository_id=repository_id)


@like_service_router.get("/get-likes/{repository_id}/", response_model=list[LikeScheme])
async def get_likes(repository_id: int, session: AsyncSession = Depends(get_like_sesison), rmq_cli: RobustConnection = Depends(get_rmq_connection), redis_cli: StrictRedis = Depends(get_redis_cli)):
    service = LikeService(session=session, rmq_cli=rmq_cli, redis_cli=redis_cli)
    return await service._get_likes_from_repository(repository_id=repository_id)



@like_service_router.get("/get-user-likes/{user_id}/", response_model=list[LikeScheme])
async def get_likes(user_id: int, session: AsyncSession = Depends(get_like_sesison), rmq_cli: RobustConnection = Depends(get_rmq_connection), redis_cli: StrictRedis = Depends(get_redis_cli)):
    service = LikeService(session=session, rmq_cli=rmq_cli, redis_cli=redis_cli)
    return await service._get_user_likes(user_id=user_id)



@like_service_router.delete("/delete-like/{like_id}/")
async def delete_like(like_id: int, session: AsyncSession = Depends(get_like_sesison), current_user: SUser = Depends(get_current_user)):
    service = LikeService(session = session, current_user = current_user)
    return await service._delete_like(like_id=like_id)


