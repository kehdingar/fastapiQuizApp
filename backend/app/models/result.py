from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlmodel import Field, SQLModel
from datetime import datetime


class Result(SQLModel, table=True):
    __tablename__ = "results"

    id: int = Field(sa_column=Column(Integer, primary_key=True, index=True))
    total: int = Field(sa_column=Column(Integer))
    quiz_id: int = Field(sa_column=Column(Integer, ForeignKey("quizzes.id")))
    user_id: int = Field(sa_column=Column(Integer, ForeignKey("users.id")))
    score: int = Field(sa_column=Column(Integer))
    submitted_at: datetime = Field(sa_column=Column(DateTime, default=datetime.now))