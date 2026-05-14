"""Pydantic schemas for API request/response validation."""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

# --- Auth ---
class UserBase(BaseModel):
    email: str

class UserResponse(UserBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}

class AuthStatus(BaseModel):
    authenticated: bool
    email: Optional[str] = None

# --- Emails ---
class EmailLogBase(BaseModel):
    gmail_msg_id: str
    sender: str
    subject: str
    snippet: str
    classification: str
    confidence_score: int
    ai_reasoning: str

class EmailLogResponse(EmailLogBase):
    id: int
    final_action: Optional[str] = None
    processed_at: datetime

    model_config = {"from_attributes": True}

class ScanResultsResponse(BaseModel):
    scan_id: int
    scan_number: int
    important: List[EmailLogResponse]
    needs_review: List[EmailLogResponse]
    unimportant: List[EmailLogResponse]

class OverrideRequest(BaseModel):
    classification: str # "important" or "unimportant"

# --- History ---
class ScanHistoryBase(BaseModel):
    scan_number: int
    total_emails: int
    important_count: int
    needs_review_count: int
    unimportant_count: int
    deleted_count: int

class ScanHistoryResponse(ScanHistoryBase):
    id: int
    scanned_at: datetime

    model_config = {"from_attributes": True}

# --- Settings ---
class SettingsResponse(BaseModel):
    confidence_threshold: int
    ai_model_name: str

class SettingsUpdateRequest(BaseModel):
    confidence_threshold: Optional[int] = None
    ai_model_name: Optional[str] = None
