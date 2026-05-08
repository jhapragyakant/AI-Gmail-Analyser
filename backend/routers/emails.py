from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import User
from backend.services.gmail_service import test_fetch_emails
from backend.services.ai_classifier import classify_email, AIClassification

router = APIRouter(prefix="/emails", tags=["Emails"])

class EmailTestRequest(BaseModel):
    sender: str
    subject: str
    body: str

@router.get("/test-fetch")
def test_fetch(email: str, db: Session = Depends(get_db)):
    """Temporary test endpoint to fetch 5 emails for a user."""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    if not user.gmail_access_token:
        raise HTTPException(status_code=400, detail="User not authenticated with Gmail")
        
    from backend.config import get_settings
    settings = get_settings()
        
    creds_dict = {
        'token': user.gmail_access_token,
        'refresh_token': user.gmail_refresh_token,
        'token_uri': "https://oauth2.googleapis.com/token",
        'client_id': settings.GOOGLE_CLIENT_ID,
        'client_secret': settings.GOOGLE_CLIENT_SECRET,
        'scopes': ['https://www.googleapis.com/auth/gmail.modify']
    }
    
    try:
        emails = test_fetch_emails(creds_dict)
        return {"emails": emails}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test-classify", response_model=AIClassification)
async def test_classify(request: EmailTestRequest):
    """
    Test endpoint to classify a sample email content.
    """
    try:
        result = classify_email(
            sender=request.sender,
            subject=request.subject,
            body=request.body
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

