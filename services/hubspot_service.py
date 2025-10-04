"""
HubSpot CRM integration for pushing contacts.
Easy to change: Add more properties or associations.
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("HUBSPOT_API_KEY")
BASE_URL = "https://api.hubapi.com/crm/v3"

def create_contact(properties: dict) -> bool:
    """
    Create a contact in HubSpot.
    properties: e.g., {'email': 'test@example.com', 'firstname': 'John', 'company': 'ABC Inc'}
    Returns: True on success.
    """
    if not API_KEY:
        print("HubSpot API key missing - skipping.")
        return False
    
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(f"{BASE_URL}/objects/contacts", json={'properties': properties}, headers=headers)
        response.raise_for_status()
        print("Contact pushed to HubSpot.")
        return True
    except requests.RequestException as e:
        print(f"HubSpot error: {e}")
        return False