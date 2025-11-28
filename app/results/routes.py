from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from datetime import datetime
from app.database import get_db
from app.auth.routes import get_current_user
from app.users.models import User
from app.results.models import Report
from app.queries.models import Query

router = APIRouter()

class ReportDetail(BaseModel):
    id: int
    title: str
    report_text: str
    question: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class ReportSummary(BaseModel):
    id: int
    query_id: int
    title: str
    question: str
    created_at: datetime
    
    class Config:
        from_attributes = True

@router.get("/{report_id}", response_model=ReportDetail)
async def get_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific report by ID.
    Only allows users to access their own reports.
    """
    report = db.query(Report).filter(
        Report.id == report_id,
        Report.user_id == current_user.id
    ).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    query = db.query(Query).filter(Query.id == report.query_id).first()
    
    return ReportDetail(
        id=report.id,
        title=report.title,
        report_text=report.report_text,
        question=query.question if query else "",
        created_at=report.created_at
    )

@router.get("/", response_model=List[ReportSummary])
async def get_all_reports(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all reports for the current user.
    Returns a list of report summaries ordered by creation date.
    """
    reports = db.query(Report).filter(
        Report.user_id == current_user.id
    ).order_by(Report.created_at.desc()).all()
    
    result = []
    for report in reports:
        query = db.query(Query).filter(Query.id == report.query_id).first()
        result.append(ReportSummary(
            id=report.id,
            query_id=report.query_id,
            title=report.title,
            question=query.question if query else "",
            created_at=report.created_at
        ))
    
    return result
