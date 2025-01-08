from fastapi import HTTPException
from apps.like_service.models import LikeModel
from redis import StrictRedis
from aio_pika import RobustConnection
from sqlalchemy.ext.asyncio import AsyncSession
from utils.scheme import SUser
from utils.utils import get_logger, consume_data
from apps.like_service.scheme import LikeScheme, RepositoryScheme, SUser
from fastapi.encoders import jsonable_encoder
from typing import Type, TypeVar
from sqlalchemy import select
import httpx
import json
import asyncio



T = TypeVar("T")

log =  get_logger()


class LikeService:
    def __init__(self, session: AsyncSession, redis_cli: StrictRedis = None, rmq_cli: RobustConnection = None, current_user: SUser = None):
        self.session = session
        self.rmq_cli = rmq_cli
        self.redis_cli = redis_cli
        self.current_user = current_user

    
    async def _create_like(self, repository_id: int):
        exist_like = (await self.session.execute(
            select(LikeModel)
            .filter_by(user_id = self.current_user.id, repository_id = repository_id)
        )).scalars().first()

        if exist_like:
            log.info("User all ready liked on this repository %s", repository_id)
            raise HTTPException(
                detail=f"You allready liked on this repository {repository_id}",
                status_code=403
            )
        
        like = LikeModel(
            repository_id=repository_id,
            user_id=self.current_user.id
        )

        self.session.add(like)
        await self.session.commit()

        return {"Detail": "Like Succsesfully created"}

    async def _get_likes_from_repository(self, repository_id: int):
        cached_data = await self._get_data_from_cache(f"get-likes-from-repository-{repository_id}")
        if cached_data:
            log.info("Returing data from cache %s", cached_data)
            return [LikeScheme(**like) for like in cached_data]

        likes = (await self.session.execute(
            select(LikeModel)
            .filter_by(repository_id = repository_id)
        )).scalars().all()

        if not likes:
            log.info("Likes not found %s", repository_id)
            return []
        
        await asyncio.gather(
            *[
                self._request_to_url(f"http://localhost:8081/user/api/v1/get-user/{like.user_id}/")
                for like in likes
            ]
        )


        user_data_json = await asyncio.gather(
            *[
                consume_data(f"get-user-by-id-{like.user_id}", connection=self.rmq_cli)
                for like in likes
            ]
        )


        user_schemes = [
            SUser(**(data if isinstance(data, dict) else json.loads(data)))
            for data in user_data_json
        ]

        
        response = [
            LikeScheme(**like.__dict__, user=user)
            for like, user in zip(likes, user_schemes)
        ]

        serialized_json = jsonable_encoder(response)

        await self.redis_cli.setex(f"get-likes-from-repository-{repository_id}", 300, json.dumps(serialized_json))
        

        return response

    async def _get_user_likes(self, user_id: int):
        cached_data = await self.redis_cli.get(f"get-user-likes-{user_id}")
        if cached_data:
            log.info("Returing data from cache")
            return [LikeScheme(**repository) for repository in json.loads(cached_data)]

        likes = (await self.session.execute(
            select(LikeModel)
            .filter_by(user_id = user_id)
        )).scalars().all()

        if not likes:
            log.info("Likes not found for user %s", user_id)
            return []


        await asyncio.gather(
            *[
                self._request_to_url(f"http://localhost:8082/repository/service/api/v1/get-repository/{like.repository_id}/")
                for like in likes
            ]
        )


        repository_data_json = await asyncio.gather(
            *[
                consume_data(f"get-repository-{like.repository_id}", connection=self.rmq_cli)
                for like in likes
            ]
        )


        repository_schemes = [
            RepositoryScheme(**(data if isinstance(data, dict) else json.loads(data)))
            for data in repository_data_json
        ]

        
        response = [
            LikeScheme(**like.__dict__, repository=repository)
            for like, repository in zip(likes, repository_schemes)
        ]

        serialized_json = jsonable_encoder(response)

        await self.redis_cli.setex(f"get-user-likes-{user_id}", 300, json.dumps(serialized_json))
        return response
    

    async def _delete_like(self, like_id: int):
        like = (await self.session.execute(
            select(LikeModel)
            .filter_by(id=like_id, user_id=self.current_user.id)
        )).scalars().first()


        if not like:
            log.info("Like not found %s", like_id)
            raise HTTPException(
                detail="Like not found",
                status_code=404
            )
        
        await self.session.delete(like)
        await self.session.commit()
        return {"detail": "Deleted Succsesfully"}
    
    
    
    async def _get_data_from_cache(self, key):
        cached_data = await self.redis_cli.get(key)
        if cached_data:
            return json.loads(cached_data)
        return None
    
    
    async def _request_to_url(self, url):
        async with httpx.AsyncClient() as cl:
            response = await cl.get(url)
            return response
        return None
    
    