from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import HTTPAuthorizationCredentials
from fastapi import APIRouter,Security
from app.models.result import Result
from app.api.utils.database import get_db
from app.api.utils.users import JWTBearer

router = APIRouter()

@router.get("/{id}",status_code=status.HTTP_200_OK,response_model=Result)
def get_result_by_id(id: int, db: Session = Depends(get_db),credentials: HTTPAuthorizationCredentials = Security(JWTBearer())):
    result = db.query(Result).filter(Result.id == id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    return result