from dotenv import load_dotenv,find_dotenv
from fastapi import Depends
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from app.models.user import User
from app.api.utils.database import get_db
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import ExpiredSignatureError,jwt
from fastapi import Request, HTTPException
import os

dotenv_path = find_dotenv(raise_error_if_not_found=True, usecwd=True)
load_dotenv(dotenv_path)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    return user

def get_user_by_id(id: int, db: Session = Depends(get_db)):
    print(f"\n\n\n DBBBBBBB {db}")
    user = db.query(User).filter(User.id == id).first()
    return user

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, os.environ.get("SECRET_KEY"), algorithm=os.environ.get("ALGORITHM"))
    return encoded_jwt

class JWTBearer(HTTPBearer):

    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code=403, detail={"status": "Forbidden", "message": "Invalid authentication schema."})
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(
                    status_code=403, detail={"status": "Forbidden", "message": "Invalid token or expired token."})
            return credentials.credentials
        else:
            raise HTTPException(
                status_code=403, detail={"status": "Forbidden", "message": "Invalid authorization code."})

    @staticmethod
    def verify_jwt(jwt_token: str):
        try:
            return True if jwt.decode(jwt_token, os.environ.get("SECRET_KEY"), algorithms=[os.environ.get("ALGORITHM")]) is not None else  None
        except ExpiredSignatureError as e:
            raise HTTPException(
                    status_code=403, detail={"status": "Forbidden", "message": "Your Session has expired. Please login to renew","ref":"exp"})

def extract_token(token: str):
    return jwt.decode(token, os.environ.get("SECRET_KEY"), algorithms=[os.environ.get("ALGORITHM")])