from sqlalchemy import Column, Integer, String,DateTime
from sqlmodel import ForeignKey, SQLModel, Relationship
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from app.models.quiz import Quiz
from app.models.user import User


class Report(SQLModel, table=True):
    __tablename__ = "reports"
    id: int = Field(sa_column=Column("id", Integer, primary_key=True, index=True))
    title: str = Field(sa_column=Column("title", String, index=True))
    description: Optional[str] = Field(sa_column=Column("description", String))
    user_id: int = Field(sa_column=Column("user_id", ForeignKey('users.id')))
    quiz_id: int = Field(sa_column=Column("quiz_id", ForeignKey('quizzes.id')))
    created_at: datetime = Field(default_factory=datetime.now)
    modified_at: datetime = Field(
        sa_column=Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    )
    users: Optional["User"] = Relationship(back_populates="reports")
    quizzes: Optional["Quiz"] = Relationship(back_populates="reports")