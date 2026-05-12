from fastapi import APIRouter, Depends, HTTPException, Cookie
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User
from ..services.gmail_service import get_auth_url, get_credentials_from_code, test_fetch_emails

router = APIRouter(prefix="/auth", tags=["auth"])

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
        user_name = profile.get('names', [{}])[0].get('displayName', 'User')
        user_picture = profile.get('photos', [{}])[0].get('url', '')
        
        if not user_email:
            raise HTTPException(status_code=400, detail="Could not retrieve email address")
            
        user = db.query(User).filter(User.email == user_email).first()
        if not user:
            user = User(email=user_email)
            db.add(user)
            
        user.gmail_access_token = creds_dict['token']
        user.gmail_refresh_token = creds_dict['refresh_token']
        
        db.commit()
        
        # In a real app, we would use a proper session/JWT. 
        # For this demo, we'll use a cookie to "login" the user.
        response = RedirectResponse(url="/")
        response.set_cookie(key="user_email", value=user_email, max_age=3600*24)
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/status")
def get_auth_status(db: Session = Depends(get_db), user_email: str = Cookie(None)):
    """Check if the user is authenticated."""
    return _get_status_internal(db, user_email)

def _get_status_internal(db: Session, user_email: str):
    if not user_email:
        return {"authenticated": False}
    
    user = db.query(User).filter(User.email == user_email).first()
    if not user or not user.gmail_access_token:
        return {"authenticated": False}
    
    return {
        "authenticated": True,
        "user": {
            "email": user.email,
            "name": user.email.split('@')[0], # Fallback name
        }
    }

@router.get("/logout")
def logout():
    """Clear the user session."""
    response = RedirectResponse(url="/")
    response.delete_cookie("user_email")
    return response

@router.post("/logout")
def logout_post():
    """Clear the user session via POST."""
    return {"message": "Logged out"}

