from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate,UserCreateResponse
from app.api.utils.database import get_db
from app.api.utils.users import get_user, get_password_hash

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



