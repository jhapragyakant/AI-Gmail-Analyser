from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User
from ..services.gmail_service import get_auth_url, get_credentials_from_code, test_fetch_emails

router = APIRouter(prefix="/auth", tags=["auth"])
emails_router = APIRouter(prefix="/emails", tags=["emails"])

@router.get("/login")
def login():
    """Redirect to Google OAuth2 consent screen."""
    return RedirectResponse(url=get_auth_url())

@router.get("/callback")
def auth_callback(code: str, db: Session = Depends(get_db)):
    """Handle OAuth2 callback and store credentials."""
    try:
        creds_dict = get_credentials_from_code(code)
        
        from googleapiclient.discovery import build
        from google.oauth2.credentials import Credentials
        from backend.config import get_settings
        
        settings = get_settings()
        
        creds = Credentials(
            token=creds_dict['token'],
            refresh_token=creds_dict['refresh_token'],
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
            scopes=['https://www.googleapis.com/auth/gmail.modify']
        )
        
        gmail = build('gmail', 'v1', credentials=creds)
        profile = gmail.users().getProfile(userId='me').execute()
        user_email = profile.get('emailAddress')
        
        if not user_email:
            raise HTTPException(status_code=400, detail="Could not retrieve email address")
            
        user = db.query(User).filter(User.email == user_email).first()
        if not user:
            user = User(email=user_email)
            db.add(user)
            
        user.gmail_access_token = creds_dict['token']
        user.gmail_refresh_token = creds_dict['refresh_token']
        
        db.commit()
        
        return {"message": "Successfully authenticated", "email": user_email}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@emails_router.get("/test-fetch")
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
