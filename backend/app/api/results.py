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

@router.get("/user/{user_id}",status_code=status.HTTP_200_OK)
def get_result_by_user_id(user_id: int, db: Session = Depends(get_db),credentials: HTTPAuthorizationCredentials = Security(JWTBearer())):
    report = db.query(Result).filter(Result.user_id == user_id).all()
    if not report:
        raise HTTPException(status_code=404, detail="Result not found for user")    
    return report