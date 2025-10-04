"""
Shared utilities: Exports, follow-up checks, date helpers, etc.
Easy to change: Add new functions here for cross-service use.
"""
import os
import json
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime, timedelta
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from models import Outreach, OutreachResponse
from services.gmail_service import send_email
from services.openai_service import generate_ai_email

load_dotenv()

def check_and_send_followups(db: Session):
    """
    Check outreaches >5 days old with no response and send AI-generated follow-up.
    Call from backend cron or manually.
    Returns: Number of follow-ups sent.
    """
    five_days_ago = datetime.utcnow() - timedelta(days=5)
    old_outreaches = db.query(Outreach).filter(
        Outreach.response == OutreachResponse.NO_RESPONSE,
        Outreach.date < five_days_ago
    ).all()
    
    sent_count = 0
    for outreach in old_outreaches:
        stakeholder = outreach.stakeholder  # Assume relationship loaded
        if stakeholder and stakeholder.email:
            follow_up_msg = generate_ai_email(
                stakeholder.name, stakeholder.company.name if stakeholder.company else '', 'Follow-up JV Opportunity'
            )
            if send_email(stakeholder.email, 'Follow-up: JV Partnership', follow_up_msg):
                outreach.response = OutreachResponse.FOLLOW_UP_NEEDED
                outreach.follow_up_date = datetime.utcnow()
                db.commit()
                sent_count += 1
    
    return sent_count

def export_to_csv(data: list[dict], filename: str = "jv_data"):
    """
    Export list of dicts to CSV download (used in Streamlit/backend).
    """
    df = pd.DataFrame(data)
    csv = df.to_csv(index=False)
    return csv  # Streamlit can st.download_button with this

def export_to_pdf(data: list[dict], filename: str = "jv_report", title: str = "JV Report"):
    """
    Generate simple PDF report.
    """
    c = canvas.Canvas(f"{filename}.pdf", pagesize=letter)
    c.drawString(100, 750, title)
    y = 700
    for item in data:
        c.drawString(100, y, str(item))
        y -= 20
        if y < 50:
            c.showPage()
            y = 750
    c.save()
    return f"{filename}.pdf"  # Path for download

def format_date(date_str: str) -> str:
    """
    Helper: Format ISO date to readable string.
    """
    return datetime.fromisoformat(date_str).strftime("%Y-%m-%d %H:%M")

# HubSpot push (optional, called from routers)
def push_to_hubspot(contact_data: dict):
    """
    Push contact to HubSpot CRM.
    """
    from services.hubspot_service import create_contact  # Import here to avoid circular
    create_contact(contact_data)