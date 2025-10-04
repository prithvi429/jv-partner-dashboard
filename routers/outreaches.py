from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from datetime import datetime

from database import get_db
from models import Outreach, Stakeholder, OutreachResponse

router = APIRouter(prefix="/outreaches", tags=["Outreaches"])

class OutreachCreate(BaseModel):
    stakeholder_id: int
    message: str
    notes: str = ""

class OutreachUpdateResponse(BaseModel):
    response: OutreachResponse
    notes: str = ""

@router.post("/", response_model=dict)
def create_outreach(outreach: OutreachCreate, db: Session = Depends(get_db)):
    stakeholder = db.query(Stakeholder).filter(Stakeholder.id == outreach.stakeholder_id).first()
    if not stakeholder:
        raise HTTPException(status_code=404, detail="Stakeholder not found")
    new_outreach = Outreach(
        stakeholder_id=outreach.stakeholder_id,
        message=outreach.message,
        notes=outreach.notes,
        date=datetime.utcnow(),
        response=OutreachResponse.NO_RESPONSE
    )
    db.add(new_outreach)
    db.commit()
    db.refresh(new_outreach)
    return {"id": new_outreach.id, "message": "Outreach created"}

@router.get("/", response_model=List[dict])
def list_outreaches(db: Session = Depends(get_db)):
    outreaches = db.query(Outreach).all()
    return [
        {
            "id": o.id,
            "stakeholder_id": o.stakeholder_id,
            "message": o.message,
            "notes": o.notes,
            "date": o.date.isoformat(),
            "response": o.response.value,
            "follow_up_date": o.follow_up_date.isoformat() if o.follow_up_date else None,
        }
        for o in outreaches
    ]

@router.put("/{outreach_id}/response")
def update_outreach_response(outreach_id: int, update: OutreachUpdateResponse, db: Session = Depends(get_db)):
    outreach = db.query(Outreach).filter(Outreach.id == outreach_id).first()
    if not outreach:
        raise HTTPException(status_code=404, detail="Outreach not found")
    outreach.response = update.response
    outreach.notes = update.notes
    db.commit()
    return {"message": "Outreach response updated"}