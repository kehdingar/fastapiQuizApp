from sqlalchemy import Column, Integer, String, Boolean,DateTime
from sqlmodel import SQLModel, Field, Relationship
from typing import List
from datetime import datetime
from fastapi import HTTPException
from pydantic import field_validator


from enum import Enum

class Role(str, Enum):
    INSTRUCTOR = "Instructor"
    STUDENT = "Student"

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: int = Field(sa_column=Column("id", Integer, primary_key=True, index=True))
    email: str = Field(sa_column=Column("email", String, unique=True))
    password: str = Field(sa_column=Column("password", String))
    role: Role = Field(sa_column=Column("role", String, default=Role.STUDENT))
    is_active: bool = Field(sa_column=Column("is_active", Boolean, default=True))
    is_superuser: bool = Field(sa_column=Column("is_superuser", Boolean, default=False))
    created_at: datetime = Field(sa_column=Column("created_at", DateTime, default=datetime.now))
    modified_at: datetime = Field(sa_column=Column("modified_at", DateTime, default=datetime.now, onupdate=datetime.now, nullable=False))



@field_validator("role")
def validate_role(cls, role: Role):
    # go to database and check user role
    if role not in [Role.INSTRUCTOR, Role.STUDENT]:
        raise HTTPException(status_code=400, detail="Invalid role. Please choose Instructor or Student.")
    return role