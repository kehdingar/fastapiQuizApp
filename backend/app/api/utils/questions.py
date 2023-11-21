from sqlalchemy.orm import Session
from app.models.question import Question, Option

def fetch_question_by_id(question_id: int, db: Session):
    """
    Fetch questions from the database based on the ID.
    """
    question = db.query(Question).filter(Question.id == question_id).first()
    return question

def fetch_questions_by_category(category_id: int, db: Session):
    """
    Fetch questions from the database based on the category ID.
    """    
    questions = db.query(Question).filter(Question.category_id == category_id).all()

    question_ids = [question.id for question in questions]
    
    results = db.query(Option).filter(Option.question_id.in_(question_ids)).all()

    question_dict = []

    for question in questions:
        # Using a list comprehension to create a list of option answers
        options = [option.answer for option in results if option.question_id == question.id]

        # Store the question and the options in the question_dict
        question_dict.append({'id':question.id,'text':question.text,'options':options})

    return question_dict


def update_question_by_id(question_id:int,payload:dict,db: Session):
    question = fetch_question_by_id(question_id,db)
    if question:
        for field, value in payload.items():
            setattr(question, field, value)
    db.commit()
    db.refresh(question)
    return question
