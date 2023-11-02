
from fastapi import APIRouter,Depends
from typing import List
from app.api.utils.categories import  fetch_all_categories
from fastapi import APIRouter
from app.api.utils.database import get_db
from sqlalchemy.orm import Session
from app.models.category import Category


router = APIRouter()

@router.get("/", response_model=List[Category])
async def get_categories(db: Session = Depends(get_db)):
    categories = fetch_all_categories(db)
    return categories
