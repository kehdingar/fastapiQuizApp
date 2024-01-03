from fastapi import APIRouter, Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.models.report import Report
from app.api.utils.database import get_db
from app.api.utils.users import JWTBearer, extract_token, get_user_by_id
from app.models.result import Result
from app.api.utils.quiz import fetch_quiz_by_id
from app.schemas.report import ReportCreate


router = APIRouter()


def get_report(db: Session, report_id: int):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    return report

# Routes
@router.get("/")
def get_reports(db: Session = Depends(get_db),credentials: HTTPAuthorizationCredentials = Security(JWTBearer())):
    token = extract_token(credentials)
    if token['role'] != "Instructor":
        raise HTTPException(status_code=403, detail="Not enough previledges")
    reports = db.query(Report).all()
    if not reports:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No Report found")
    return reports

@router.get("/{report_id}",status_code=status.HTTP_200_OK)
def get_report_by_id(report_id: int, db: Session = Depends(get_db),credentials: HTTPAuthorizationCredentials = Security(JWTBearer())):
    report = get_report(db, report_id)
    return report

@router.get("/user/{user_id}",status_code=status.HTTP_200_OK)
def get_report_by_user_id(user_id: int, db: Session = Depends(get_db),credentials: HTTPAuthorizationCredentials = Security(JWTBearer())):
    token = extract_token(credentials)
    if token['role'] != "Instructor":
        raise HTTPException(status_code=403, detail="Not enough previledges")
    result = db.query(Result).filter(Result.user_id == user_id).all()
    report = db.query(Report).filter(Report.user_id == user_id).all()
    db_report = {'result':result,'report':report}
    return db_report

@router.get("/quiz/{quiz_id}",status_code=status.HTTP_200_OK)
def get_report_by_quiz_id(quiz_id: int, db: Session = Depends(get_db),credentials: HTTPAuthorizationCredentials = Security(JWTBearer())):
    quiz = fetch_quiz_by_id(quiz_id,db)
    if not quiz:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz not found")
    result = db.query(Result).filter(Result.quiz_id == quiz_id).first()
    report = db.query(Report).filter(Report.quiz_id == quiz_id).first()
    db_report = {'result':result,'report':report}
    return db_report

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=Report)
def create_report(report: ReportCreate, db: Session = Depends(get_db),credentials: HTTPAuthorizationCredentials = Security(JWTBearer())):
    token = extract_token(credentials)
    if token['role'] != "Instructor":
        raise HTTPException(status_code=403, detail="Not enough previledges")
    quiz_id = report.quiz_id

    quiz = fetch_quiz_by_id(quiz_id,db)
    if not quiz:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz not found")
    db_report = Report(**report.model_dump())
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report