"""SQLAlchemy ORM models."""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    gmail_access_token = Column(String, nullable=True)
    gmail_refresh_token = Column(String, nullable=True)
    token_expiry = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    scan_history = relationship("ScanHistory", back_populates="user", cascade="all, delete")

class ScanHistory(Base):
    __tablename__ = "scan_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    total_emails = Column(Integer, default=0)
    important_count = Column(Integer, default=0)
    needs_review_count = Column(Integer, default=0)
    unimportant_count = Column(Integer, default=0)
    deleted_count = Column(Integer, default=0)
    scanned_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="scan_history")
    emails = relationship("EmailLog", back_populates="scan", cascade="all, delete")

class EmailLog(Base):
    __tablename__ = "email_log"

    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scan_history.id"))
    gmail_msg_id = Column(String, index=True, nullable=False)
    sender = Column(String)
    subject = Column(String)
    snippet = Column(Text)
    classification = Column(String) # "important" | "needs_review" | "unimportant"
    confidence_score = Column(Integer) # 0-100
    ai_reasoning = Column(Text)
    final_action = Column(String, nullable=True) # "kept" | "trashed" | "overridden_to_important" | "overridden_to_unimportant"
    processed_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    scan = relationship("ScanHistory", back_populates="emails")
