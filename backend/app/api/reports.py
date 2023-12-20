from fastapi import APIRouter, Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.models.report import Report
from app.api.utils.database import get_db
from app.api.utils.users import JWTBearer, extract_token


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