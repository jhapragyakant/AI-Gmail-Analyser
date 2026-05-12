# Prompt to Start Development

Copy the prompt below and paste it as your **first message** to the AI assistant on your personal account. Before sending, **attach the `AI_GMAIL_ANALYSER_CONTEXT.md` file** so the AI has full context.

---

## How to Use

1. Open your AI coding assistant on your personal account
2. Attach the file `AI_GMAIL_ANALYSER_CONTEXT.md` (from this same folder)
3. Copy everything inside the prompt block below and paste it as your first message
4. Send it

---

## The Prompt

```
I want to build the AI Gmail Analyser project. I have attached a context file (AI_GMAIL_ANALYSER_CONTEXT.md) that contains the COMPLETE architecture, design decisions, tech stack, database schema, API endpoints, AI classifier design, frontend design, and a phased build order for this project.

Read the entire context file carefully. That file IS the implementation plan — every decision has already been made. Do not re-ask questions that are already answered in it.

Key things to note from the context:
- This is a FastAPI + Vanilla HTML/CSS/JS web dashboard
- AI-only classification using Gemini 2.5 Flash (no manual rules engine)
- Three-tier system: Important (85%+ confident) / Needs Review (below 85%) / Unimportant (85%+ confident)
- "Delete" means move to Gmail Trash (30-day recovery), NEVER permanent delete
- If the AI is unsure even slightly, the email goes to "Needs Review" — never auto-delete uncertain emails
- The confidence threshold is 85% and must be configurable via the Settings UI
- The AI model must be swappable (change model via config without rewriting code)
- V1 scope: single Gmail account, unread emails only

I want to build this project following the phased build order in the context file:
- Phase 0: Environment & GCP Setup
- Phase 1: Project Foundation
- Phase 2: Gmail OAuth2 & Email Fetching
- Phase 3: AI Classifier (Standalone)
- Phase 4: Full Scan Pipeline
- Phase 5: Frontend Dashboard
- Phase 6: Polish & Edge Cases
- Phase 7: Deployment

IMPORTANT: We will build ONE PHASE AT A TIME. After each phase, I will test it using the test checkpoints described in the context file. Only after I confirm a phase works should you move to the next phase.

The project should be created in the current workspace directory.

Let's start with Phase 0. Walk me through the GCP setup step by step, and tell me exactly what credentials I need to have ready before we move to Phase 1.
```

---

## For Subsequent Phases

After completing each phase and testing it, just send:

```
Phase [N] is working. Let's move to Phase [N+1].
```

If something doesn't work during testing, send:

```
Phase [N] test failed. Here's what happened: [describe the error/issue]
```

The AI will have all the context it needs from the attached file to debug and fix issues within the current phase before moving on.
