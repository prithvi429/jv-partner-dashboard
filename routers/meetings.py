from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from datetime import datetime

from database import get_db
from models import Meeting, Outreach, MeetingStatus

router = APIRouter(prefix="/meetings", tags=["Meetings"])

class MeetingCreate(BaseModel):
    outreach_id: int
    scheduled_date: datetime
    participants: str
    agenda: str

class MeetingUpdateStatus(BaseModel):
    status: MeetingStatus

@router.post("/", response_model=dict)
def create_meeting(meeting: MeetingCreate, db: Session = Depends(get_db)):
    outreach = db.query(Outreach).filter(Outreach.id == meeting.outreach_id).first()
    if not outreach:
        raise HTTPException(status_code=404, detail="Outreach not found")
    new_meeting = Meeting(
        outreach_id=meeting.outreach_id,
        scheduled_date=meeting.scheduled_date,
        participants=meeting.participants,
        agenda=meeting.agenda,
        status=MeetingStatus.SCHEDULED
    )
    db.add(new_meeting)
    db.commit()
    db.refresh(new_meeting)
    return {"id": new_meeting.id, "message": "Meeting scheduled"}

@router.get("/", response_model=List[dict])
def list_meetings(db: Session = Depends(get_db)):
    meetings = db.query(Meeting).all()
    return [
        {
            "id": m.id,
            "outreach_id": m.outreach_id,
            "scheduled_date": m.scheduled_date.isoformat(),
            "participants": m.participants,
            "agenda": m.agenda,
            "status": m.status.value,
        }
        for m in meetings
    ]

@router.put("/{meeting_id}/status")
def update_meeting_status(meeting_id: int, update: MeetingUpdateStatus, db: Session = Depends(get_db)):
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    meeting.status = update.status
    db.commit()
    return {"message": "Meeting status updated"}