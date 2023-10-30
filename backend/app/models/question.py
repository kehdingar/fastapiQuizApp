from typing import Optional,List
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey,Boolean
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime

class Question(SQLModel, table=True):
    __tablename__ = 'questions'

    id: int = Field(sa_column=Column("id", Integer, primary_key=True, index=True))
    text: str = Field(sa_column=Column(String))
    created_at: datetime = Field(sa_column=Column("created_at", DateTime, default=datetime.now))
    modified_at: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(DateTime, onupdate=datetime.now, nullable=False))
    
    category_id: int = Field(sa_column=Column(Integer, ForeignKey("categories.id",ondelete="CASCADE")))
    quiz_id: Optional[int] = Field(sa_column=Column(Integer, ForeignKey("quizzes.id")))
    categories: Optional["Category"] = Relationship(back_populates="questions")
    quizzes: Optional["Quiz"] = Relationship(back_populates="questions")
    options: List["Option"] = Relationship(back_populates="questions")

class Option(SQLModel, table=True):
    __tablename__ = 'options'

    id: int = Field(sa_column=Column("id", Integer, primary_key=True, index=True))
    answer: str = Field(sa_column=Column(String))
    is_correct: bool = Field(sa_column=Column(Boolean, default=False))
    question_id: int = Field(sa_column=Column(Integer, ForeignKey("questions.id")))
    questions: Optional["Question"] = Relationship(back_populates="options")
