import json
import logging
from google import genai
from pydantic import BaseModel
from backend.config import get_settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIClassification(BaseModel):
    important: bool          # True = important, False = unimportant
    confidence: int          # 0-100
    reasoning: str           # One-line explanation
    classification: str      # "important" | "needs_review" | "unimportant"

def determine_classification(ai_result: dict, threshold: int = 85) -> str:
    """Map AI result to one of the three tiers based on confidence."""
    is_important = ai_result.get("important", True)
    confidence = ai_result.get("confidence", 0)
    
    if is_important and confidence >= threshold:
        return "important"
    elif not is_important and confidence >= threshold:
        return "unimportant"
    else:
        return "needs_review"

def classify_email(sender: str, subject: str, body: str) -> AIClassification:
    """
    Calls Gemini AI to classify an email.
    """
    settings = get_settings()
    
    if not settings.GEMINI_API_KEY:
        logger.error("GEMINI_API_KEY not found in settings")
        return AIClassification(
            important=True,
            confidence=0,
            reasoning="AI configuration missing (API Key).",
            classification="needs_review"
        )

    try:
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        
        # Truncate body to 2000 chars as per context
        truncated_body = body[:2000] if body else ""
        
        prompt = f"""
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
{{
  "important": true/false,
  "confidence": <0-100>,
  "reasoning": "<one sentence explaining your decision>"
}}

---
From: {sender}
Subject: {subject}
Body (first 2000 chars): {truncated_body}
"""

        response = client.models.generate_content(
            model=settings.AI_MODEL_NAME,
            contents=prompt,
            config={
                "response_mime_type": "application/json"
            }
        )
        
        # Extract JSON from response
        # Using response.text to get the content
        ai_json = json.loads(response.text)
        
        # Determine the bucket
        bucket = determine_classification(ai_json, settings.CONFIDENCE_THRESHOLD)
        
        return AIClassification(
            important=ai_json.get("important", True),
            confidence=ai_json.get("confidence", 0),
            reasoning=ai_json.get("reasoning", "No reasoning provided."),
            classification=bucket
        )
    except Exception as e:
        logger.exception("AI Classification failed")
        # Fallback to Needs Review if AI fails or returns invalid JSON
        return AIClassification(
            important=True,
            confidence=0,
            reasoning=f"AI Classification failed: {str(e)}",
            classification="needs_review"
        )
