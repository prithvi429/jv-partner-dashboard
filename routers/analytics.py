from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Outreach, OutreachResponse, Meeting
from datetime import datetime, timedelta

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/kpis")
def get_kpis(db: Session = Depends(get_db)):
    """
    Return key performance indicators:
    - Total outreaches sent
    - Response rate (%)
    - Interested leads count
    - Meetings scheduled count
    """
    total_outreach = db.query(Outreach).count()
    responded = db.query(Outreach).filter(Outreach.response != OutreachResponse.NO_RESPONSE).count()
    interested = db.query(Outreach).filter(Outreach.response == OutreachResponse.INTERESTED).count()
    meetings_scheduled = db.query(Meeting).filter(Meeting.status == "scheduled").count()

    response_rate = (interested / responded * 100) if responded > 0 else 0

    return {
        "total_outreach": total_outreach,
        "response_rate_percent": round(response_rate, 2),
        "interested_leads": interested,
        "meetings_scheduled": meetings_scheduled,
    }

@router.get("/outreach_breakdown")
def outreach_response_breakdown(db: Session = Depends(get_db)):
    """
    Return counts of outreach responses by category.
    """
    counts = {}
    for response in OutreachResponse:
        counts[response.value] = db.query(Outreach).filter(Outreach.response == response).count()
    return counts

@router.get("/outreach_over_time")
def outreach_over_time(days: int = 30, db: Session = Depends(get_db)):
    """
    Return outreach counts per day for the last `days` days.
    """
    cutoff = datetime.utcnow() - timedelta(days=days)
    results = (
        db.query(Outreach.date)
        .filter(Outreach.date >= cutoff)
        .all()
    )
    # Aggregate counts per day
    counts = {}
    for (date,) in results:
        day = date.date().isoformat()
        counts[day] = counts.get(day, 0) + 1
    # Return sorted list of dicts
    return [{"date": day, "count": count} for day, count in sorted(counts.items())]