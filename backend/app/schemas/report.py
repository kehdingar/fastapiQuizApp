from typing import Optional
from pydantic import BaseModel

class ReportBase(BaseModel):
    title: str
    description: Optional[str] = None
    quiz_id: int
    user_id: int

class ReportCreate(ReportBase):
    pass

class ReportUpdate(ReportBase):
    pass

class Report(ReportBase):
    id: int

    class Config:
        orm_mode = True