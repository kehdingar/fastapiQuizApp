
from typing import List
from fastapi import APIRouter,Depends, HTTPException,status
from app.models.quiz import Quiz
from app.api.auth import get_user
from sqlalchemy.orm import Session
from fastapi import APIRouter,Security
from fastapi.security import HTTPAuthorizationCredentials
from app.api.utils.database import get_db
from app.api.utils.users import JWTBearer, extract_token
from app.api.utils.questions import fetch_question_by_id, fetch_questions_by_category, update_question_by_id
from app.api.utils.quiz import fetch_quiz_by_id
from app.models.result import Result

router = APIRouter()

@router.post("/", response_model=dict,status_code=status.HTTP_201_CREATED)
async def create_quiz(payload:  dict,db: Session = Depends(get_db),credentials: HTTPAuthorizationCredentials = Security(JWTBearer())):
    
    quiz_name = payload.get("name")
    category_id = payload.get("category_id")
    question_ids = payload.get("question_ids")


    token = extract_token(credentials)

    instructor = get_user(db=db, email=token['email'])
    del payload['name']
    del payload['question_ids']

    db_quiz = Quiz(name=quiz_name,instructor=instructor.id,category_id=category_id)
    db.add(db_quiz)
    db.commit()
    db.refresh(db_quiz)
    quiz_id = db_quiz.id
    payload['quiz_id'] = quiz_id
    for question_id in question_ids:
        update_question_by_id(question_id,payload,db)

    return {'id':db_quiz.id}

@router.get("/id/{quiz_id}",response_model=List[dict])
async def get_quiz(quiz_id: int,db: Session = Depends(get_db)):
    quiz = fetch_quiz_by_id(quiz_id,db)
    if quiz is not None:
        results = fetch_questions_by_category(quiz.category_id,db)
        return results
    raise HTTPException(status_code=404, detail="Quiz not found")

@router.post("/evaluate", status_code=status.HTTP_201_CREATED)
async def evaluate_quiz(payload: dict,db: Session = Depends(get_db)):
    user = payload['user_id']
    submission = payload['submission'] # dictionary of question_id:answer
    quiz_id = payload['quiz_id']

    score = 0
    for question_id,answer in submission.items():
        # Unpacking results, and the comma indicates is unpacking a
        # of exactly one object
        question = fetch_question_by_id(question_id,db)
        if question.options[0].question_id == int(question_id):
            if question.options[0].answer == answer:
                score += 1
    total = len(submission)
    score_data = Result(quiz_id=quiz_id,user_id=user,score=score,total=total)
    db.add(score_data)
    db.commit()
    db.refresh(score_data)
    return {'user':user, "quiz_id":quiz_id, "score":score,"total":total}