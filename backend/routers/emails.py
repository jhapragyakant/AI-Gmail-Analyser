from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
import time

from backend.database import get_db
from backend.models import User, ScanHistory, EmailLog
from backend.services.gmail_service import fetch_unread_emails, trash_email
from backend.services.ai_classifier import classify_email
from backend.schemas import ScanResultsResponse, OverrideRequest, EmailLogResponse
from backend.config import get_settings

router = APIRouter(prefix="/emails", tags=["Emails"])

def get_current_user_creds(email: str, db: Session):
    user = db.query(User).filter(User.email == email).first()
    if not user or not user.gmail_access_token:
        raise HTTPException(status_code=400, detail="User not authenticated with Gmail")
    
    settings = get_settings()
    return {
        'token': user.gmail_access_token,
        'refresh_token': user.gmail_refresh_token,
        'token_uri': "https://oauth2.googleapis.com/token",
        'client_id': settings.GOOGLE_CLIENT_ID,
        'client_secret': settings.GOOGLE_CLIENT_SECRET,
        'scopes': ['https://www.googleapis.com/auth/gmail.modify']
    }, user

@router.post("/scan")
def scan_emails(email: str, db: Session = Depends(get_db)):
    creds_dict, user = get_current_user_creds(email, db)
    
    try:
        # Reduced from 50 to 10 to avoid long timeouts and respect free tier rate limits
        raw_emails = fetch_unread_emails(creds_dict, max_results=10)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch emails: {e}")

    if not raw_emails:
        return {"scan_id": None, "message": "No unread emails found."}

    scan_record = ScanHistory(
        user_id=user.id,
        total_emails=len(raw_emails)
    )
    db.add(scan_record)
    db.commit()
    db.refresh(scan_record)

    important_count = 0
    needs_review_count = 0
    unimportant_count = 0

    for mail in raw_emails:
        ai_result = classify_email(
            sender=mail['sender'],
            subject=mail['subject'],
            body=mail['body']
        )
        
        # Rate Limiter: Sleep for 4 seconds between requests
        # Gemini free tier allows 15 requests per minute (1 request every 4 seconds)
        time.sleep(4)
        
        log = EmailLog(
            scan_id=scan_record.id,
            gmail_msg_id=mail['id'],
            sender=mail['sender'],
            subject=mail['subject'],
            snippet=mail['snippet'],
            classification=ai_result.classification,
            confidence_score=ai_result.confidence,
            ai_reasoning=ai_result.reasoning,
            final_action="kept" if ai_result.classification == "important" else None
        )
        db.add(log)
        
        if ai_result.classification == "important":
            important_count += 1
        elif ai_result.classification == "needs_review":
            needs_review_count += 1
        else:
            unimportant_count += 1

    scan_record.important_count = important_count
    scan_record.needs_review_count = needs_review_count
    scan_record.unimportant_count = unimportant_count
    db.commit()

    return {"scan_id": scan_record.id, "message": "Scan completed successfully."}

@router.get("/results/{scan_id}", response_model=ScanResultsResponse)
def get_scan_results(scan_id: int, db: Session = Depends(get_db)):
    scan_record = db.query(ScanHistory).filter(ScanHistory.id == scan_id).first()
    if not scan_record:
        raise HTTPException(status_code=404, detail="Scan not found")

    emails = db.query(EmailLog).filter(EmailLog.scan_id == scan_id).all()
    
    important = [e for e in emails if e.classification == "important"]
    needs_review = [e for e in emails if e.classification == "needs_review"]
    unimportant = [e for e in emails if e.classification == "unimportant"]

    return ScanResultsResponse(
        scan_id=scan_id,
        important=important,
        needs_review=needs_review,
        unimportant=unimportant
    )

@router.patch("/{log_id}/override")
def override_classification(log_id: int, override: OverrideRequest, db: Session = Depends(get_db)):
    log = db.query(EmailLog).filter(EmailLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Email log not found")

    if override.classification not in ["important", "unimportant"]:
        raise HTTPException(status_code=400, detail="Invalid classification override")

    old_classification = log.classification
    log.classification = override.classification
    log.final_action = f"overridden_to_{override.classification}"
    
    scan = db.query(ScanHistory).filter(ScanHistory.id == log.scan_id).first()
    if scan:
        if old_classification == "important":
            scan.important_count -= 1
        elif old_classification == "needs_review":
            scan.needs_review_count -= 1
        elif old_classification == "unimportant":
            scan.unimportant_count -= 1
            
        if override.classification == "important":
            scan.important_count += 1
        elif override.classification == "unimportant":
            scan.unimportant_count += 1
            
    db.commit()
    return {"message": "Classification overridden successfully"}

@router.post("/cleanup")
def cleanup_emails(scan_id: int, email: str, db: Session = Depends(get_db)):
    creds_dict, user = get_current_user_creds(email, db)
    
    scan_record = db.query(ScanHistory).filter(ScanHistory.id == scan_id, ScanHistory.user_id == user.id).first()
    if not scan_record:
        raise HTTPException(status_code=404, detail="Scan not found")
        
    unimportant_emails = db.query(EmailLog).filter(
        EmailLog.scan_id == scan_id,
        EmailLog.classification == "unimportant",
        (EmailLog.final_action != "trashed") | (EmailLog.final_action == None)
    ).all()
    
    deleted_count = 0
    for log in unimportant_emails:
        success = trash_email(creds_dict, log.gmail_msg_id)
        if success:
            log.final_action = "trashed"
            deleted_count += 1
            
    scan_record.deleted_count += deleted_count
    db.commit()
    
    return {"message": f"Cleaned up {deleted_count} emails.", "deleted_count": deleted_count}


