
from fastapi import APIRouter,Depends,HTTPException,status,Security
from typing import List
from fastapi.security import HTTPAuthorizationCredentials
from app.api.utils.categories import  fetch_all_categories,fetch_all_category_by_id
from fastapi import APIRouter
from app.api.utils.database import get_db
from sqlalchemy.orm import Session
from app.models.category import Category
from app.api.utils.users import JWTBearer, extract_token
from app.schemas.category import CategoryCreate


router = APIRouter()

@router.get("/", response_model=List[Category])
async def get_categories(db: Session = Depends(get_db)):
    categories = fetch_all_categories(db)
    return categories

@router.get("/{category_id}", response_model=Category)
async def get_category(category_id: int,db: Session = Depends(get_db)):
    category = fetch_all_category_by_id(category_id,db)
    if category:
        return category
    raise HTTPException(status_code=404, detail="Category not found")

@router.post("/", status_code=status.HTTP_201_CREATED,response_model=Category)
async def create_category(category:CategoryCreate,db: Session = Depends(get_db),credentials: HTTPAuthorizationCredentials = Security(JWTBearer())):
    token = extract_token(credentials)
    if token['role'] != "Instructor":
        raise HTTPException(status_code=403, detail="Not enough previledges")    
    category = Category(name=category.name)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category