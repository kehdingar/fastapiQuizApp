from sqlalchemy.orm import Session
from app.models.question import Question

def fetch_question_by_id(question_id: int, db: Session):
    """
    Fetch questions from the database based on the ID.
    """
    question = db.query(Question).filter(Question.id == question_id).first()
    return question