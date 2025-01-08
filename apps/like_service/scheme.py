from pydantic import BaseModel
from utils.scheme import SUser
from typing import Optional
from datetime import datetime


class RepositoryScheme(BaseModel):
    id: int
    repository_title: Optional[str] = None
    is_private: Optional[bool] = None
    about: Optional[str] = None
    user_id: Optional[int] = None
    user: Optional[SUser] = None
    created_at: datetime



class LikeScheme(BaseModel):
    id: int
    user: Optional[SUser] = None
    repository: Optional[RepositoryScheme] = None
    created_at: datetime
