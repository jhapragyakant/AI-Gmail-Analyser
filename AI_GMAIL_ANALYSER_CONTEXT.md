# AI Gmail Analyser — Full Project Context

> **Purpose of this file:** This document contains the complete context, architecture, and implementation plan for the AI Gmail Analyser project. Feed this entire file to your AI coding assistant to give it full context before starting development. A ready-to-use prompt is provided at the bottom.

---

## Project Overview

I want to build a **web application** that connects to my Gmail account, reads my unread emails, and uses AI to decide whether each email is important, unimportant, or needs my review. The app should let me review the AI's decisions on a web dashboard, override any mistakes, and then trash the unimportant ones.

### The Problem
- I receive too many emails daily — some important, some not
- I can't read all of them
- Emails from the same sender can be both important AND unimportant (e.g., Amazon sends order confirmations AND promotional spam)
- I need an AI that understands the *content* of each email, not just the sender

### The Solution
A web dashboard that:
1. Connects to Gmail via OAuth2
2. Fetches unread emails
3. Uses Google Gemini AI to classify each email with a confidence score
4. Sorts emails into three tiers: Important / Needs Review / Unimportant
5. Lets me review and override classifications
6. Trashes confirmed-unimportant emails (move to Trash, recoverable for 30 days)

---

## All Design Decisions (Locked In)

| Decision | Answer | Reasoning |
|---|---|---|
| Classification approach | **AI-only** — no manual rules engine | AI handles everything autonomously; simpler codebase |
| AI model | **Gemini 2.5 Flash** | Fast, cheap, good at classification. Must be swappable to upgrade later |
| Confidence threshold | **85%** (configurable via UI) | Only emails where AI is 85%+ confident get auto-classified; everything else goes to "Needs Review" |
| Safety principle | **If AI is unsure even a bit, DON'T delete** | Unsure emails go to "Needs Review" for manual decision |
| "Needs Review" handling | Shown as a separate middle column on dashboard | User manually moves them to Important or Unimportant |
| Deletion behavior | **Move to Gmail Trash** (NOT permanent delete) | 30-day recovery window; safety net for AI mistakes |
| Scan scope (V1) | **Unread emails only** | Read emails will be added in V2 |
| Backend | **FastAPI** (Python 3.11+) | Async, fast, auto-generated API docs |
| Frontend | **Vanilla HTML / CSS / JavaScript** | No framework overhead; premium dark-mode UI with glassmorphism |
| Database | **SQLite** (dev) → **PostgreSQL** (prod) | Zero-config locally, production-grade in the cloud |
| ORM | **SQLAlchemy 2.0** + Alembic | Models & migrations |
| Email API | **Gmail API** via `google-api-python-client` | OAuth2-based, web-app friendly (not IMAP) |
| Deployment | **TBD** (Render / Railway / Cloud Run) | Will be decided later |
| Gmail accounts | **Single account** (V1) | Multiple accounts in V2 |
| GCP project | **Don't have one** — need full step-by-step setup guide | Guide is included in this plan |

---

## Architecture

```
                    ┌─────────────────────────────────────────┐
                    │              Cloud Server               │
                    │                                         │
   You (Browser) ──►  Frontend (HTML/CSS/JS)                 │
                    │      │                                  │
                    │      ▼                                  │
                    │  Backend API (FastAPI)                  │
                    │      │         │         │              │
                    │      ▼         ▼         ▼              │
                    │  Gmail API   Gemini    Database         │
                    │  (OAuth2)    (AI)     (SQLite/PG)       │
                    └─────────────────────────────────────────┘
```

### User Flow
1. Open dashboard → Click "Connect Gmail" → OAuth2 consent screen
2. Click "Scan Inbox" → Backend fetches **unread** emails
3. AI classifies every email → confidence score + reasoning
4. Dashboard shows **three columns**: Important (green) · Needs Review (amber) · Unimportant (red)
5. Review "Needs Review" emails → move left (keep) or right (trash)
6. Click "Clean Up" → unimportant emails moved to Gmail Trash

### Three-Tier Classification (Confidence-Based)

| Confidence Range | Bucket | What Happens |
|---|---|---|
| **85–100%** confident it's important | ✅ **Important** | Kept in inbox |
| **Below 85%** on either side | 🤔 **Needs Review** | Shown to user to decide |
| **85–100%** confident it's unimportant | 🗑️ **Unimportant** | Queued for trash (user confirms) |

---

## Tech Stack

| Layer | Technology | Package/Version |
|---|---|---|
| Backend | FastAPI | `fastapi`, `uvicorn[standard]` |
| Database | SQLAlchemy 2.0 | `sqlalchemy`, `alembic` |
| Config | Pydantic Settings | `pydantic-settings` |
| Gmail | Gmail API | `google-api-python-client`, `google-auth`, `google-auth-oauthlib` |
| AI | Gemini 2.5 Flash | `google-genai` |
| Frontend | Vanilla HTML/CSS/JS | No dependencies |
| Env | python-dotenv | `python-dotenv` |

---

## Project Structure

```
ai-gmail-analyser/
├── backend/
│   ├── main.py                  # FastAPI app entry point
│   ├── config.py                # Environment & settings (Pydantic Settings)
│   ├── database.py              # DB engine, session factory, Base
│   ├── models.py                # SQLAlchemy ORM models
│   ├── schemas.py               # Pydantic request/response schemas
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py              # Gmail OAuth2 login / callback / logout
│   │   └── emails.py            # Scan, list results, override, cleanup
│   ├── services/
│   │   ├── __init__.py
│   │   ├── gmail_service.py     # Gmail API wrapper (fetch, trash, mark read)
│   │   └── ai_classifier.py     # AI model integration (swappable)
│   ├── requirements.txt
│   └── .env.template
├── frontend/
│   ├── index.html               # Single-page dashboard
│   ├── css/
│   │   └── styles.css           # Full design system
│   └── js/
│       ├── app.js               # Main app logic & state management
│       ├── api.js               # REST API call helpers
│       └── ui.js                # DOM rendering & animations
├── .env.template
├── Dockerfile                   # For cloud deployment (later)
└── README.md
```

---

## Database Schema

### USER table
| Column | Type | Notes |
|---|---|---|
| id | int | PK |
| email | string | Gmail address |
| gmail_access_token | string | OAuth2 access token |
| gmail_refresh_token | string | OAuth2 refresh token |
| token_expiry | datetime | When the access token expires |
| created_at | datetime | Account creation time |

### SCAN_HISTORY table
| Column | Type | Notes |
|---|---|---|
| id | int | PK |
| user_id | int | FK → USER |
| total_emails | int | How many emails were scanned |
| important_count | int | |
| needs_review_count | int | |
| unimportant_count | int | |
| deleted_count | int | How many were actually trashed |
| scanned_at | datetime | |

### EMAIL_LOG table
| Column | Type | Notes |
|---|---|---|
| id | int | PK |
| scan_id | int | FK → SCAN_HISTORY |
| gmail_msg_id | string | Gmail's message ID |
| sender | string | |
| subject | string | |
| snippet | string | Preview text |
| classification | string | "important" / "needs_review" / "unimportant" |
| confidence_score | int | 0-100 |
| ai_reasoning | string | One-line AI explanation |
| final_action | string | "kept" / "trashed" / "overridden_to_important" / "overridden_to_unimportant" |
| processed_at | datetime | |

---

## AI Classifier Design

### Swappable Model Architecture
The AI classifier must be built as a service with a clean interface so the model can be swapped later:

```python
class AIClassification:
    important: bool          # True = important, False = unimportant
    confidence: int          # 0-100
    reasoning: str           # One-line explanation
    classification: str      # "important" | "needs_review" | "unimportant"

def classify_email(sender, subject, body, model="gemini-2.5-flash") -> AIClassification:
    ...
```

### AI Prompt
```
You are an email importance classifier. Analyze the email below and determine
if it is IMPORTANT or UNIMPORTANT to the recipient.

RULES:
1. Be extremely conservative. When in doubt, lean toward IMPORTANT.
2. Only mark as UNIMPORTANT if you are highly confident it is:
   - Marketing / promotional content with no actionable information
   - Mass newsletters the user didn't explicitly sign up for
   - Automated notifications with no action required (e.g., "your weekly summary")
   - Spam or phishing attempts
3. ALWAYS mark as IMPORTANT if the email:
   - Contains OTPs, verification codes, or security alerts
   - Is about financial transactions, orders, or deliveries
   - Appears to be from a real person (not automated)
   - Contains deadlines, appointments, or action items
   - Is work-related or professional correspondence

Respond ONLY in this JSON format:
{
  "important": true/false,
  "confidence": <0-100>,
  "reasoning": "<one sentence explaining your decision>"
}

---
From: {sender}
Subject: {subject}
Body (first 2000 chars): {body}
```

### Confidence → Classification Mapping
```python
def determine_classification(ai_result, threshold=85):
    if ai_result.important and ai_result.confidence >= threshold:
        return "important"
    elif not ai_result.important and ai_result.confidence >= threshold:
        return "unimportant"
    else:
        return "needs_review"
```

---

## Gmail API — Full Setup Guide (One-Time)

### Step 1 — Create a Google Cloud Project
1. Go to https://console.cloud.google.com/
2. Click the project dropdown at the top → "New Project"
3. Name it "AI Gmail Analyser"
4. Click Create and wait
5. Make sure the new project is selected in the dropdown

### Step 2 — Enable the Gmail API
1. Left sidebar → APIs & Services → Library
2. Search for "Gmail API"
3. Click on it → click "Enable"

### Step 3 — Configure the OAuth Consent Screen
1. APIs & Services → OAuth consent screen
2. Choose "External" user type → Create
3. Fill in: App name: "AI Gmail Analyser", support email: your email, developer email: your email
4. Save and Continue
5. Scopes page: Add `https://www.googleapis.com/auth/gmail.readonly` and `https://www.googleapis.com/auth/gmail.modify`
6. Save and Continue
7. Test users page: Add your Gmail address → Save and Continue
8. Back to Dashboard

### Step 4 — Create OAuth2 Credentials
1. APIs & Services → Credentials
2. "+ Create Credentials" → "OAuth client ID"
3. Application type: Web application
4. Name: "AI Gmail Analyser Web Client"
5. Authorized redirect URIs: add `http://localhost:8000/auth/callback`
6. Click Create
7. Copy Client ID and Client Secret — these go in your .env file

### Step 5 — Get a Gemini API Key
1. Go to https://aistudio.google.com/apikey
2. Click "Create API Key"
3. Copy the key — this goes in your .env file as GEMINI_API_KEY

---

## API Endpoints

### Auth
| Method | Endpoint | Description |
|---|---|---|
| GET | /auth/login | Redirects to Google OAuth2 consent screen |
| GET | /auth/callback | Handles OAuth2 callback, stores tokens in DB |
| GET | /auth/status | Returns whether user is authenticated + email |
| POST | /auth/logout | Clears stored tokens |

### Emails
| Method | Endpoint | Description |
|---|---|---|
| POST | /emails/scan | Fetches unread emails, runs AI classification on each |
| GET | /emails/results/{scan_id} | Returns classified emails grouped by tier |
| PATCH | /emails/{log_id}/override | User moves email between tiers |
| POST | /emails/cleanup | Trashes all confirmed-unimportant emails |

### History
| Method | Endpoint | Description |
|---|---|---|
| GET | /history | List past scans with summary stats |
| GET | /history/{scan_id} | Full email-by-email log of a scan |

### Settings
| Method | Endpoint | Description |
|---|---|---|
| GET | /settings | Get current settings (threshold, model, etc.) |
| PUT | /settings | Update settings |

---

## Frontend Dashboard Design

### Three main views:

**View 1 — Scan & Review (Home)**
- "Scan Inbox" button at top
- Three-column layout after scan: Important (green) | Needs Review (amber) | Unimportant (red)
- Each email card: sender, subject, snippet, confidence badge, AI reasoning, arrow buttons to move between columns
- "Clean Up" button with confirmation modal

**View 2 — Scan History**
- Table of past scans with expandable rows

**View 3 — Settings**
- Connected account + disconnect
- Confidence threshold slider (default: 85)
- AI model selector dropdown

### Design Direction
- Dark mode default with glassmorphism card panels
- Color palette: deep navy/slate background, green/amber/red accents
- Inter font (Google Fonts)
- Smooth transitions, micro-animations, loading skeletons
- Responsive (mobile: columns stack vertically)
- Premium, modern look — NOT a basic MVP

---

## Build Order — Sequential (Build → Test → Iterate)

Each phase must be completed and tested before moving to the next.

### Phase 0 — Environment & GCP Setup
**Build:** Install Python 3.11+, follow GCP setup guide above, get all credentials
**Test:** Confirm you have Client ID, Client Secret, Gemini API key, Gmail API enabled, test user added
**Move on when:** All credentials ready

### Phase 1 — Project Foundation
**Build:** Folder structure, venv, dependencies, config.py, database.py, models.py, schemas.py, minimal main.py
**Test:** `uvicorn main:app --reload` → Swagger docs load at localhost:8000/docs, SQLite DB file created
**Move on when:** Server starts, DB exists, Swagger works

### Phase 2 — Gmail OAuth2 & Email Fetching
**Build:** routers/auth.py, services/gmail_service.py, temp test endpoint GET /emails/test-fetch
**Test:** Login via /auth/login → Google consent → callback → /auth/status shows email → /emails/test-fetch returns real unread emails
**Move on when:** Can log in and see real unread emails as JSON

### Phase 3 — AI Classifier (Standalone)
**Build:** services/ai_classifier.py, temp test endpoint POST /emails/test-classify
**Test:** POST sample emails → get correct classifications with confidence scores and reasoning
**Move on when:** AI correctly classifies 3+ test emails across all 3 tiers

### Phase 4 — Full Scan Pipeline
**Build:** POST /emails/scan, GET /emails/results/{scan_id}, PATCH override, POST cleanup, GET history. Remove temp endpoints.
**Test:** Full pipeline via Swagger: scan → view results → override → cleanup → check Gmail Trash → view history
**Move on when:** End-to-end backend works via API

### Phase 5 — Frontend Dashboard
**Build incrementally:** 5a: Design system + shell → 5b: Auth UI → 5c: Scan & Review page → 5d: History & Settings
**Test each sub-phase visually** before moving to the next
**Move on when:** Complete app works end-to-end through the UI

### Phase 6 — Polish & Edge Cases
**Build:** Error handling, loading states, empty inbox state, double-scan prevention, responsive polish
**Test:** Break things on purpose — no internet, 0 emails, double-click, mobile viewport
**Move on when:** App is robust

### Phase 7 — Deployment (when ready)
**Build:** Dockerfile, choose platform, production env vars, SQLite → PostgreSQL, deploy
**Test:** App works at production URL with real Gmail

---

## V1 Does NOT Include (Future Versions)

| Feature | Version |
|---|---|
| Scan read emails | V2 |
| Multiple Gmail accounts | V2 |
| AI fine-tuned to personal data | V2 |
| Auto-generated categories/labels | V2 |
| Scheduled automatic scans | V2 |
| Email digest/summary reports | V2 |
| User-defined rules engine | V2 (if needed) |
| Mobile app | V3+ |

---

## Important Safety Requirements
1. **NEVER permanently delete emails** — always move to Trash (30-day recovery)
2. **If AI confidence is below 85%, classify as "needs_review"** — never auto-delete uncertain emails
3. **Always require user confirmation** before trashing emails (confirmation modal)
4. **Log every decision** in the EMAIL_LOG table with the AI's reasoning
5. **OAuth2 tokens must be stored securely** — never in code, always in .env / database
6. **Never commit .env or credentials to git**
