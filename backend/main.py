"""AI Gmail Analyser — FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from . import models

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Gmail Analyser",
    description="Backend API for classifying and managing emails using AI.",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Update for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "AI Gmail Analyser API is running."}

# Include Routers
from .routers import auth
app.include_router(auth.router)
app.include_router(auth.emails_router)
