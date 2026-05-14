from fastapi import APIRouter, Depends, HTTPException, Cookie
from sqlalchemy.orm import Session
from typing import Optional
from ..database import get_db
from ..models import User
from ..schemas import SettingsResponse, SettingsUpdateRequest

router = APIRouter(prefix="/settings", tags=["Settings"])

@router.get("", response_model=SettingsResponse)
def get_user_settings(db: Session = Depends(get_db), user_email: Optional[str] = Cookie(None)):
    if not user_email:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    return SettingsResponse(
        confidence_threshold=user.confidence_threshold,
        ai_model_name=user.ai_model
    )

@router.patch("")
def update_user_settings(settings: SettingsUpdateRequest, db: Session = Depends(get_db), user_email: Optional[str] = Cookie(None)):
    if not user_email:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    if settings.ai_model_name:
        user.ai_model = settings.ai_model_name
    if settings.confidence_threshold is not None:
        user.confidence_threshold = settings.confidence_threshold
        
    db.commit()
    return {"message": "Settings updated successfully"}
