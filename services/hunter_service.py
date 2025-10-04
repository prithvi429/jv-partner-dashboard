"""
Hunter.io service for email verification and domain search.
Easy to change: Update API endpoint or add caching here.
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("HUNTER_API_KEY")
BASE_URL = "https://api.hunter.io/v2"

def verify_email(email: str) -> dict:
    """
    Verify if an email is deliverable.
    Returns: {'result': 'deliverable' | 'undeliverable' | ...} or {} on error.
    """
    if not API_KEY:
        return {}
    
    url = f"{BASE_URL}/email-verifier"
    params = {"email": email, "api_key": API_KEY}
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Hunter.io verification error: {e}")
        return {}

def search_domain_emails(domain: str) -> dict:
    """
    Search emails for a company domain.
    Returns: {'emails': [...]} or {} on error.
    """
    if not API_KEY:
        return {}
    
    url = f"{BASE_URL}/domain-search"
    params = {"domain": domain, "api_key": API_KEY}
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Hunter.io domain search error: {e}")
        return {}