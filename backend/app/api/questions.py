from fastapi import APIRouter, HTTPException, Depends, status, Security
from typing import List
from app.api.utils.users import JWTBearer, extract_token
from app.models.user import Role
from app.api.utils.database import get_db
from sqlalchemy.orm import Session
from fastapi.security import HTTPAuthorizationCredentials
from app.schemas.question import QuizQuestionCreate
from app.models.category import Category
from app.models.question import Option, Question
from app.api.utils.questions import fetch_questions_by_category


router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED,)
async def create_question(
    questions: List[QuizQuestionCreate],
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Security(JWTBearer())
):
    
    token = extract_token(credentials)
    role = token['role']
    if role != Role.INSTRUCTOR:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient privileges")

    # Extract data from the request payload
    added_questions_database = []
    added_options_database = []
    category_id = questions[0].question.category_id
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category does not exist")

    for question in questions:
        text = question.question.text
        # Create a new question instance
        new_question = Question(
            text=text,
            category_id=question.question.category_id
        )
        db.add(new_question)
        db.commit()  # Commit the question to generate its id
        added_questions_database.append(new_question)

        # Saving Options
        for option in question.options:
            new_option = Option(
                question_id=new_question.id,
                answer=option.answer,
                is_correct=option.is_correct
            )
            db.add(new_option)
            added_options_database.append(new_option)
    
    db.commit()

    # Refresh all added questions in the database session
    for new_question in added_questions_database:
        db.refresh(new_question)

    # Refresh all added options in the database session
    for new_option in added_options_database:
        db.refresh(new_option)
    
    # Return the created question with options in the response
    return questions

@router.get("/category/{category_id}",)
async def get_question_by_category(category_id: int,db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id).first()

    if not category:
        raise HTTPException(status_code=404, detail="Category does not exist")
    questions = fetch_questions_by_category(category_id,db)

    if not questions:
        raise HTTPException(status_code=404, detail="No questions found for the specified category")
    return questions