"""
Calendly service for scheduling meetings.
Easy to change: Add custom questions or webhooks here.
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("CALENDLY_TOKEN")
BASE_URL = "https://api.calendly.com"

def schedule_meeting(email: str, name: str, event_uri: str) -> dict:
    """
    Create a Calendly invitee/event.
    event_uri: From .env (e.g., your event type ID).
    Returns: API response or {} on error.
    """
    if not TOKEN:
        return {}
    
    headers = {
        'Authorization': f'Bearer {TOKEN}',
        'Content-Type': 'application/json'
    }
    data = {
        'invitee': {'email': email, 'name': name, 'create': 1},
        'event_type': event_uri
    }
    
    try:
        response = requests.post(f"{BASE_URL}/scheduled_events", json=data, headers=headers)
        response.raise_for_status()