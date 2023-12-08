from pydantic import BaseModel

class ResultCreate(BaseModel):
    total: int
    user_id: int
    quiz_id: int
    score: int
