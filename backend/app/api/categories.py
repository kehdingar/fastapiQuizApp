
from fastapi import APIRouter,Depends,HTTPException
from typing import List
from app.api.utils.categories import  fetch_all_categories,fetch_all_category_by_id
from fastapi import APIRouter
from app.api.utils.database import get_db
from sqlalchemy.orm import Session
from app.models.category import Category


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