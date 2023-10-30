from typing import Optional, List
from sqlalchemy import Column, Integer, String
from sqlmodel import Field, Relationship
from sqlmodel import SQLModel


class Category(SQLModel, table=True):
    __tablename__ = 'categories'

    id: int = Field(sa_column=Column("id", Integer, primary_key=True, index=True))
    name: str = Field(sa_column=Column("name", String))

    questions: Optional[List["Question"]] = Relationship(back_populates="categories")
    quizzes: Optional["Quiz"] = Relationship(back_populates="categories")