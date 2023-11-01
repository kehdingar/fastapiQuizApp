from dotenv import load_dotenv,find_dotenv
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate,UserCreateResponse, UserLogin, UserResetPassword
from app.api.utils.database import get_db
from app.api.utils.users import get_user, get_password_hash,verify_password,create_access_token
from app.api.utils.email import send_password_reset_email
from datetime import timedelta
import os


dotenv_path = find_dotenv(raise_error_if_not_found=True, usecwd=True)
load_dotenv(dotenv_path)

router = APIRouter()

@router.post("/register", status_code=status.HTTP_201_CREATED,response_model=UserCreateResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user(db=db, email=user.email)
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    user.password = get_password_hash(user.password)
    db_user = User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/login",status_code=status.HTTP_202_ACCEPTED)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = get_user(db=db, email=user_data.email)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not Found")
    if not verify_password(user_data.password,user.password ):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect email or password")
    access_token_expires = timedelta(minutes=int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES")))
    access_token = create_access_token(data={"email": user.email,"role":user.role}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "Bearer"}

@router.post("/reset-password")
def reset_password(user_email: UserResetPassword, db: Session = Depends(get_db)):
    user = get_user(db=db, email=user_email.email)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email not registered")
    token = create_access_token(data={"email": user.email}, expires_delta=timedelta(hours=1))
    send_password_reset_email(user_email.email, token)
    return {"detail": "Password reset email sent"}






