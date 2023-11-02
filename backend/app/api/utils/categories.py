from sqlalchemy.orm import Session
from app.models.category import Category
from sqlalchemy.orm import Session


def fetch_all_categories(db: Session):
    """
    Fetch all categories from the database.
    """
    categories = db.query(Category).all()
    return categories