from fastapi import Depends
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.models.user import User
from app.api.utils.database import get_db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    return user
