from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import ValidationError
from sqlalchemy.orm import Session
from fastapi.security import HTTPAuthorizationCredentials
from fastapi import APIRouter,Security
from app.models.result import Result
from app.api.utils.database import get_db
from app.api.utils.users import JWTBearer, extract_token, get_password_hash, get_user
from app.models.user import User
from app.schemas.user import UserCreate, UserCreateResponse


router = APIRouter()

# [include_in_schema=False] excludes this route
@router.post("/", status_code=status.HTTP_201_CREATED,response_model=UserCreateResponse,include_in_schema=False)
async def create_user(user: UserCreate, db: Session = Depends(get_db),credentials: HTTPAuthorizationCredentials = Security(JWTBearer())):
    token = extract_token(credentials)
    if token['role'] != "Instructor":
        raise HTTPException(status_code=403, detail="Not enough previledges")      
    db_user = get_user(db=db, email=user.email) 
    if db_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="email already registered")
    try:
        # Validate email using Pydantic's validator
        User(**user.model_dump())

    except ValidationError as e:
        # Extract error messages        
        error_dict = dict(e.errors())
        # Get specific email error        
        email_error = error_dict.get("email")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"email": email_error},  # Use the extracted error message
        ) from e
    user.password = get_password_hash(user.password)
    db_user = User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/",status_code=status.HTTP_200_OK)
async def get_all_users(db: Session = Depends(get_db),credentials: HTTPAuthorizationCredentials = Security(JWTBearer())):
    token = extract_token(credentials)
    if token['role'] != "Instructor":
        raise HTTPException(status_code=403, detail="Not enough previledges")        
    users = db.query(User).all()
    return users

@router.get("/{email}",status_code=status.HTTP_200_OK)
async def get_user_by_email(email: str, db: Session = Depends(get_db),credentials: HTTPAuthorizationCredentials = Security(JWTBearer())):
    token = extract_token(credentials)
    if token['role'] != "Instructor":
        raise HTTPException(status_code=403, detail="Not enough previledges")       
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.delete("/{email}",status_code=status.HTTP_200_OK)
async def delete_user(email: str, db: Session = Depends(get_db),credentials: HTTPAuthorizationCredentials = Security(JWTBearer())):
    token = extract_token(credentials)
    if token['role'] != "Instructor":
        raise HTTPException(status_code=403, detail="Not enough previledges")      
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}

