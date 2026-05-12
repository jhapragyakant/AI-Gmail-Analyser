# Phase 4 API Testing Guide

This document outlines how to test the email classification, scanning, and cleanup endpoints introduced in Phase 4.

## Prerequisites

1. Ensure your FastAPI server is running:
   ```bash
   python main.py
   ```
2. You must have already completed the OAuth2 login flow from Phase 2, so your `email` and tokens are stored in the database.

> [!TIP]
> **Interactive Swagger Docs**  
> The easiest way to test these endpoints is through the built-in FastAPI Swagger interface.
> Navigate to [http://localhost:8000/docs](http://localhost:8000/docs) in your browser. You will see a section labeled **Emails** containing all the endpoints below.

---

## 1. Scan Unread Emails

Triggers the AI to fetch and classify your unread emails.

- **Endpoint:** `POST /emails/scan`
- **Query Parameter:** `email` (Your authenticated email address)

**Using cURL:**
```bash
curl -X 'POST' \
  'http://localhost:8000/emails/scan?email=YOUR_EMAIL@gmail.com' \
  -H 'accept: application/json'
```

**Expected Response:**
```json
{
  "scan_id": 1,
  "message": "Scan completed successfully."
}
```
*(Save the `scan_id` for the next steps!)*

---

## 2. View Scan Results

Retrieves the results of a specific scan, separating emails into `important`, `needs_review`, and `unimportant`.

- **Endpoint:** `GET /emails/results/{scan_id}`
- **Path Parameter:** `scan_id` (The ID returned from the `/scan` endpoint)

**Using cURL:**
```bash
curl -X 'GET' \
  'http://localhost:8000/emails/results/1' \
  -H 'accept: application/json'
```

**Expected Response:**
You will receive a JSON object containing three lists of email logs:
```json
{
  "scan_id": 1,
  "important": [...],
  "needs_review": [...],
  "unimportant": [
    {
      "gmail_msg_id": "18a93b...",
      "sender": "newsletter@spam.com",
      "subject": "Weekly Update",
      "snippet": "Read our latest news...",
      "classification": "unimportant",
      "confidence_score": 95,
      "ai_reasoning": "Standard promotional newsletter content.",
      "id": 42,
      "final_action": null,
      "processed_at": "2026-05-12T10:00:00.000Z"
    }
  ]
}
```
*(Find an email log `id` from the response if you wish to test the override endpoint.)*

---

## 3. Override a Classification

If the AI misclassified an email, you can manually override it before cleanup.

- **Endpoint:** `PATCH /emails/{log_id}/override`
- **Path Parameter:** `log_id` (The internal database ID of the specific email log, e.g., `42`)
- **JSON Body:** `{"classification": "important"}` OR `{"classification": "unimportant"}`

**Using cURL:**
```bash
curl -X 'PATCH' \
  'http://localhost:8000/emails/42/override' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "classification": "important"
}'
```

**Expected Response:**
```json
{
  "message": "Classification overridden successfully"
}
```
*(This will update the log and the counts in the Scan History).*

---

## 4. Cleanup / Trash Unimportant Emails

> [!WARNING]
> This is a **destructive action**. It will connect to your Gmail account and move all emails classified as "unimportant" (from this specific scan) directly into your Gmail Trash.

- **Endpoint:** `POST /emails/cleanup`
- **Query Parameters:**
  - `scan_id`: The ID of the scan you reviewed.
  - `email`: Your authenticated email address.

**Using cURL:**
```bash
curl -X 'POST' \
  'http://localhost:8000/emails/cleanup?scan_id=1&email=YOUR_EMAIL@gmail.com' \
  -H 'accept: application/json'
```

**Expected Response:**
```json
{
  "message": "Cleaned up 5 emails.",
  "deleted_count": 5
}
```
