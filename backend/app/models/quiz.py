
from typing import List
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from typing import Optional



class Quiz(SQLModel, table=True):
    __tablename__ = 'quizzes'

    id: int = Field(sa_column=Column("id", Integer, primary_key=True, index=True))
    name: str = Field(sa_column=Column(String))
    instructor: int = Field(sa_column=Column(Integer, ForeignKey("users.id")))
    user: Optional[int] = Field(sa_column=Column(Integer, ForeignKey("users.id"), nullable=True))
    created_at: datetime = Field(sa_column=Column(DateTime, default=datetime.now))
    category_id: int = Field(sa_column=Column(Integer, ForeignKey("categories.id")))
    categories: Optional[List["Category"]] = Relationship(back_populates="quizzes")
    questions: Optional[List["Question"]] = Relationship(back_populates="quizzes")
    reports: List['Report'] = Relationship(back_populates="quizzes")