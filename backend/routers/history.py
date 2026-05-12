from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend.database import get_db
from backend.models import User, ScanHistory, EmailLog
from backend.schemas import ScanHistoryResponse, EmailLogResponse

router = APIRouter(prefix="/history", tags=["History"])

@router.get("", response_model=List[ScanHistoryResponse])
def get_history(email: str, db: Session = Depends(get_db)):
    """List past scans with summary stats for the user."""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    scans = db.query(ScanHistory).filter(ScanHistory.user_id == user.id).order_by(ScanHistory.scanned_at.desc()).all()
    return scans

@router.get("/{scan_id}", response_model=List[EmailLogResponse])
def get_history_scan_details(scan_id: int, email: str, db: Session = Depends(get_db)):
    """Full email-by-email log of a specific scan."""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    scan_record = db.query(ScanHistory).filter(ScanHistory.id == scan_id, ScanHistory.user_id == user.id).first()
    if not scan_record:
        raise HTTPException(status_code=404, detail="Scan not found or access denied")
        
    emails = db.query(EmailLog).filter(EmailLog.scan_id == scan_id).order_by(EmailLog.classification).all()
    return emails
