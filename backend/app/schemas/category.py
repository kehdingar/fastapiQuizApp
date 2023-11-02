from typing import Optional
from pydantic import BaseModel


class CategoryCreate(BaseModel):
    id: Optional[int] = None
    name: str