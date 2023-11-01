from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class UserBase(BaseModel):
    email: str
    # role: str

class UserCreate(UserBase):
    password: str

class UserCreateResponse(UserBase):
    role: str
    is_active: bool
    modified_at: datetime
    created_at: datetime
    is_superuser: bool
    id: int

class UserLogin(UserBase):
    password:str

class UserResetPassword(UserBase):
    pass
