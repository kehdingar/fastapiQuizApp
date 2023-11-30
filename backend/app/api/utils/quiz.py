from sqlalchemy.orm import Session
from app.models.quiz import Quiz

def fetch_quiz_by_id(quiz_id: int, db: Session):
    """
    Fetch quiz from the database based on the ID.
    """
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    return quiz