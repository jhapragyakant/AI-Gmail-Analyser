import os
import base64
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from backend.config import get_settings

settings = get_settings()

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def get_oauth_flow():
    client_config = {
        "web": {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "redirect_uris": [settings.GOOGLE_REDIRECT_URI]
        }
    }
    
    flow = Flow.from_client_config(
        client_config,
        scopes=SCOPES,
        redirect_uri=settings.GOOGLE_REDIRECT_URI
    )
    return flow

def get_auth_url():
    flow = get_oauth_flow()
    auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline')
    return auth_url

def get_credentials_from_code(code: str):
    flow = get_oauth_flow()
    flow.fetch_token(code=code)
    credentials = flow.credentials
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }

def get_gmail_service(creds_dict: dict):
    creds = Credentials(
        token=creds_dict.get('token'),
        refresh_token=creds_dict.get('refresh_token'),
        token_uri=creds_dict.get('token_uri'),
        client_id=creds_dict.get('client_id'),
        client_secret=creds_dict.get('client_secret'),
        scopes=creds_dict.get('scopes')
    )
    service = build('gmail', 'v1', credentials=creds)
    return service

def _get_email_body(payload: dict) -> str:
    """Recursively extract plain text body from the payload."""
    body = ""
    if "parts" in payload:
        for part in payload["parts"]:
            if part.get("mimeType") == "text/plain":
                data = part.get("body", {}).get("data")
                if data:
                    body += base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
            elif "parts" in part:
                body += _get_email_body(part)
    elif payload.get("mimeType") == "text/plain":
        data = payload.get("body", {}).get("data")
        if data:
            body = base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
    return body

def fetch_unread_emails(creds_dict: dict, max_results=50):
    """Fetches unread emails from the inbox."""
    service = get_gmail_service(creds_dict)
    # Query for unread emails in the inbox
    results = service.users().messages().list(userId='me', labelIds=['INBOX', 'UNREAD'], maxResults=max_results).execute()
    messages = results.get('messages', [])
    
    emails = []
    for message in messages:
        try:
            msg = service.users().messages().get(userId='me', id=message['id'], format='full').execute()
            headers = msg['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
            
            body = _get_email_body(msg['payload'])
            # Fallback to snippet if body extraction fails
            if not body:
                body = msg.get('snippet', '')
                
            emails.append({
                'id': msg['id'], 
                'subject': subject, 
                'sender': sender, 
                'snippet': msg.get('snippet', ''),
                'body': body
            })
        except Exception as e:
            print(f"Error fetching email {message['id']}: {e}")
            continue
        
    return emails

def trash_email(creds_dict: dict, msg_id: str):
    """Moves an email to the Trash."""
    service = get_gmail_service(creds_dict)
    try:
        service.users().messages().trash(userId='me', id=msg_id).execute()
        return True
    except Exception as e:
        print(f"Failed to trash email {msg_id}: {e}")
        return False

def test_fetch_emails(creds_dict: dict, max_results=5):
    """Temporary test endpoint functionality."""
    return fetch_unread_emails(creds_dict, max_results)

