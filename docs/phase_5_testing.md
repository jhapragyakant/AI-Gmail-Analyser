# Phase 5 — Comprehensive Frontend Testing Guide

This guide provides a detailed, step-by-step process to verify the functionality and aesthetics of the AI Gmail Analyser Dashboard.

## 0. Preparation
1. Ensure your `.env` file has valid `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, and `GEMINI_API_KEY`.
2. Start the server:
   ```powershell
   python main.py
   ```
3. Open your browser and navigate to `http://127.0.0.1:8000`.

---

## 1. Initial State & Authentication (Step-by-Step)

### A. The Login Screen
- **Action**: Visit `http://127.0.0.1:8000`.
- **Observe**: You should see a centered "Welcome to Gmail Analyser" card. The sidebar and top navigation bar should **not** be visible.
- **Check**: Is the "A" logo visible? Does the button say "Sign in with Google"?

### B. The OAuth Flow
- **Action**: Click the "Sign in with Google" button.
- **Observe**: You are redirected to Google's consent screen.
- **Action**: Choose your account and authorize the app.
- **Result**: After authorization, you should be redirected back to the Dashboard (`/`).
- **Observe**: The sidebar should now be visible on the left. Your name (or email prefix) should appear in the top-right corner.

---

## 2. Dashboard & Navigation

### A. View Switching
- **Action**: Click through the sidebar links: **Dashboard**, **Scan Emails**, **History**, and **Settings**.
- **Observe**:
  - The main content area should update instantly with a fade-in animation.
  - The top bar title (e.g., "Scan History") should update to match the selection.
  - The active menu item in the sidebar should be highlighted in indigo.

### B. Responsive Check
- **Action**: Shrink the browser window width to mobile size.
- **Observe**: The sidebar should collapse to icons only or hide text, and the main content should adjust its padding.

---

## 3. Running an AI Scan (The Core Feature)

### A. Starting the Scan
- **Action**: Go to the **Scan Emails** tab.
- **Action**: Select "Last 7 Days" from the dropdown.
- **Action**: Click the **Run AI Analysis** button.
- **Observe**:
  - A progress card appears with a spinning loader and a progress bar.
  - Status text should update (e.g., "Initializing connection...", "Processing emails...").
  - *Note: Since the current backend is synchronous, the UI might feel "stuck" for a few seconds while the AI works, then the results will appear.*

### B. Reviewing Results
- **Observe**: Once finished, three summary cards appear at the top (Important, Review, Unimportant).
- **Check**: Does the email list below show actual emails from your inbox?
- **Action**: Hover over an email row. It should highlight slightly.
- **Action**: Look at the "Score" column. This is the AI confidence score.

---

## 4. Interaction & Data Persistence

### A. Classification Override
- **Action**: Find an email in the "Review" or "Unimportant" category.
- **Action**: Click the **Star icon** (Mark as Important) on that row.
- **Observe**: A notification (toast) should appear at the bottom-right saying "Marked as important".
- **Action**: Verify the indicator dot for that email changes color (Green for Important).

### B. Bulk Cleanup (Trashing)
- **Action**: Click the **Trash X Emails** button at the top of the results list.
- **Action**: Click "OK" on the browser confirmation dialog.
- **Observe**: A "Cleaning up..." notification appears.
- **Result**: You should be automatically redirected to the **History** tab.

---

## 5. History & Verification

### A. History List
- **Action**: In the **History** tab, verify that your recent scan appears at the top.
- **Check**: Does it show the correct count of Important/Review/Unimportant emails?
- **Check**: Does the date and time match your current session?

### B. Logout & Security
- **Action**: Click the **Logout** button at the bottom of the sidebar.
- **Observe**: You should be redirected back to the login screen.
- **Action**: Try to navigate manually to `http://127.0.0.1:8000/history`.
- **Observe**: You should be blocked and see the Login screen again.

---

## Troubleshooting "Single Message" Error
If you still see a JSON message like `{"message": "..."}` instead of the dashboard:
1. Ensure you have deleted the `@app.get("/")` route in `backend/main.py`.
2. Hard-refresh your browser (Ctrl + F5) to clear any cached responses.
3. Check the terminal for any errors during startup.
