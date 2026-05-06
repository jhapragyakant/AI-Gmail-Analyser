# AI Gmail Analyser — Task Tracker

## Phase 0 — Environment & GCP Setup
- [x] Install Python 3.11+
- [x] Create Google Cloud project
- [x] Enable Gmail API
- [x] Configure OAuth consent screen
- [x] Create OAuth2 credentials
- [x] Get Gemini API key

## Phase 1 — Project Foundation
- [x] Create project folder structure
- [x] Create virtual environment and install dependencies
- [x] Create `.env.template`
- [x] Build `config.py`
- [x] Build `database.py`
- [x] Build `models.py`
- [x] Build `schemas.py`
- [x] Build `main.py`
- [x] Test server startup and DB creation

## Phase 2 — Gmail OAuth2 & Email Fetching
- [ ] Build `routers/auth.py`
- [ ] Build `services/gmail_service.py`
- [ ] Add temporary test endpoint `GET /emails/test-fetch`
- [ ] Wire up auth router in `main.py`

## Phase 3 — AI Classifier (Standalone)
- [ ] Build `services/ai_classifier.py`
- [ ] Implement `classify_email()`
- [ ] Implement `determine_classification()` bucketing
- [ ] Add temporary test endpoint `POST /emails/test-classify`

## Phase 4 — Full Scan Pipeline
- [ ] Build `POST /emails/scan`
- [ ] Build `GET /emails/results/{scan_id}`
- [ ] Build `PATCH /emails/{log_id}/override`
- [ ] Build `POST /emails/cleanup`
- [ ] Build `GET /history`
- [ ] Remove temporary endpoints

## Phase 5 — Frontend Dashboard
- [ ] 5a: Design System + Shell
- [ ] 5b: Auth UI
- [ ] 5c: Scan & Review Page
- [ ] 5d: History & Settings Pages

## Phase 6 — Polish & Edge Cases
- [ ] Error handling & loading states
- [ ] Rate limiting & truncation
- [ ] Double-scan prevention

## Phase 7 — Deployment
- [ ] Dockerfile
- [ ] Config for production
