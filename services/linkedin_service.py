"""
LinkedIn enrichment via Proxycurl (scraping API).
Easy to change: Switch to official LinkedIn API if available.
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("PROXYCURL_API_KEY")
BASE_URL = "https://nubela.co/proxycurl/api/linkedin"

def fetch_profile(linkedin_url: str) -> dict:
    """
    Fetch profile data (name, headline, company, etc.).
    Returns: JSON dict or {} on error.
    """
    if not API_KEY:
        return {}
    
    headers = {'Authorization': f'Bearer {API_KEY}'}
    params = {'linkedin_profile_url': linkedin_url, 'use_post_plus': 'true'}
    
    try:
        response = requests.get(BASE_URL + '/profile', headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        # Store as JSON string in DB
        return json.dumps(data)
    except requests.RequestException as e:
        print(f"Proxycurl error: {e}")
        return '{}'