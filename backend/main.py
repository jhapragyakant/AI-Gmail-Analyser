"""AI Gmail Analyser — FastAPI application entry point."""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .database import engine, Base
from . import models
from .routers import auth, emails, history, settings

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

# Include Routers
app.include_router(auth.router)
app.include_router(emails.router)
app.include_router(history.router)
app.include_router(settings.router)

# Serve Frontend

# Mount the static files (CSS, JS)
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
app.mount("/static", StaticFiles(directory=frontend_path), name="static")

@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    # If the path exists in the static directory, it will be handled by the mount above
    # But since we mount it at /static, we need to handle the root and other routes for SPA-like behavior
    file_path = os.path.join(frontend_path, full_path)
    if os.path.isfile(file_path):
        return FileResponse(file_path)
    return FileResponse(os.path.join(frontend_path, "index.html"))


