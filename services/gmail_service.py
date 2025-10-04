"""
Gmail service for sending emails via Google API.
Easy to change: Add templates or attachments here.
Requires credentials.json and token.json (auto-generated on first run).
"""
import base64
import os
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from dotenv import load_dotenv

load_dotenv()
SCOPES = ['https://www.googleapis.com/auth/gmail.send']
CREDS_FILE = 'credentials.json'
TOKEN_FILE = 'token.json'

def get_gmail_service():
    """
    Authenticate and return Gmail service.
    Auto-handles OAuth flow and token refresh.
    """
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)  # Opens browser for consent
        
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    
    return build('gmail', 'v1', credentials=creds)

def send_email(to_email: str, subject: str, body: str) -> bool:
    """
    Send an email.
    Returns: True on success, False on error.
    """
    try:
        service = get_gmail_service()
        message = f"From: me\nTo: {to_email}\nSubject: {subject}\n\n{body}"
        message_bytes = base64.urlsafe_b64encode(message.encode('utf-8')).decode()
        
        body_msg = {'raw': message_bytes}
        service.users().messages().send(userId='me', body=body_msg).execute()
        return True
    except Exception as e:
        print(f"Gmail send error: {e}")
        return False