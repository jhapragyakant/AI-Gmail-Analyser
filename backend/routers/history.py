from fastapi import APIRouter, Depends, HTTPException, Cookie
from sqlalchemy.orm import Session
from typing import List, Optional

from backend.database import get_db
from backend.models import User, ScanHistory, EmailLog
from backend.schemas import ScanHistoryResponse, EmailLogResponse

router = APIRouter(prefix="/history", tags=["History"])

@router.get("", response_model=List[ScanHistoryResponse])
def get_history(db: Session = Depends(get_db), user_email: Optional[str] = Cookie(None)):
    """List past scans with summary stats for the user."""
    if not user_email:
        raise HTTPException(status_code=401, detail="Not authenticated")
        
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    scans = db.query(ScanHistory).filter(ScanHistory.user_id == user.id).order_by(ScanHistory.scanned_at.desc()).all()
    return scans

@router.get("/{scan_id}", response_model=List[EmailLogResponse])
def get_history_scan_details(scan_id: int, db: Session = Depends(get_db), user_email: Optional[str] = Cookie(None)):
    """Full email-by-email log of a specific scan."""
    if not user_email:
        raise HTTPException(status_code=401, detail="Not authenticated")
        
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    scan_record = db.query(ScanHistory).filter(ScanHistory.id == scan_id, ScanHistory.user_id == user.id).first()
    if not scan_record:
        raise HTTPException(status_code=404, detail="Scan not found or access denied")
        
    emails = db.query(EmailLog).filter(EmailLog.scan_id == scan_id).order_by(EmailLog.classification).all()
    return emails
