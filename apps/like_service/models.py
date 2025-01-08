from sqlalchemy import Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from database.like_database import LikeBase
from datetime import datetime


class LikeModel(LikeBase):
    __tablename__ = "likes"

    id: Mapped[int] = mapped_column(Integer, index=True, primary_key=True)
    repository_id: Mapped[int] = mapped_column(Integer, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow())