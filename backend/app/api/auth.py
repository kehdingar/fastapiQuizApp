from dotenv import load_dotenv,find_dotenv
from fastapi import APIRouter, Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.models.user import User
from jose import JWTError, jwt
from app.schemas.user import UserCreate,UserCreateResponse, UserLogin, UserResetPassword, UserResetPasswordConfirm
from app.api.utils.database import get_db
from app.api.utils.users import JWTBearer, get_user, get_password_hash,verify_password,create_access_token
from app.api.utils.email import send_password_reset_email
from datetime import timedelta
import os
from .users import create_user


dotenv_path = find_dotenv(raise_error_if_not_found=True, usecwd=True)
load_dotenv(dotenv_path)

router = APIRouter()

@router.post("/register", status_code=status.HTTP_201_CREATED,response_model=UserCreateResponse)
async def register(user: UserCreate, db: Session = Depends(get_db),credentials: HTTPAuthorizationCredentials = Security(JWTBearer())):
    db_user = await create_user(user,db,credentials)
    print(f"\n\n\n DBBBBBBBBBBBBB USER : {db_user}")
    return db_user

@router.post("/login",status_code=status.HTTP_202_ACCEPTED)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = get_user(db=db, email=user_data.email)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not Found")
    if not verify_password(user_data.password,user.password ):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect email or password")
    access_token_expires = timedelta(minutes=int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES")))
    access_token = create_access_token(data={"email": user.email,"role":user.role}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "Bearer"}

@router.post("/reset-password")
async def reset_password(user_email: UserResetPassword, db: Session = Depends(get_db)):
    user = get_user(db=db, email=user_email.email)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email not registered")
    token = create_access_token(data={"email": user.email}, expires_delta=timedelta(hours=1))
    send_password_reset_email(user_email.email, token)
    return {"detail": "Password reset email sent"}


# @router.post("/reset-password-confirm")
# def reset_password_confirm(user_data: UserResetPasswordConfirm, db: Session = Depends(get_db)):
#     try:
#         payload = jwt.decode(user_data.token, os.environ.get("SECRET_KEY"), algorithms=[os.environ.get("ALGORITHM") ])
#         email = payload.get("email")
#         user = get_user(db=db, email=email)
#         if not user:
#             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email not registered")
                
#         if user.password == user_data.password:
#             raise HTTPException(status_code=status.HTTP_226_IM_USED, detail="New password same as old password. Please change password")
#         user.password = get_password_hash(user_data.password)
#         db.commit()
#         return {"detail": "Password reset successful"}
#     except JWTError:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")

@router.post("/reset-password-confirm")
async def reset_password_confirm(user_data: UserResetPasswordConfirm, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(user_data.token, os.environ.get("SECRET_KEY"), algorithms=[os.environ.get("ALGORITHM")])
        email = payload.get("email")
        user = get_user(db=db, email=email)
        if not user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email not registered")
                
        if verify_password(user_data.password, user.password):
            raise HTTPException(status_code=status.HTTP_226_IM_USED, detail="New password is the same as the old password. Please choose a different password")
        
        user.password = get_password_hash(user_data.password)
        db.commit()
        db.refresh(user)
        return {"detail": "Password reset successful"}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")


