from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from datetime import datetime

from database import get_db
from models import Deal, Meeting, DealStage

router = APIRouter(prefix="/deals", tags=["Deals"])

class DealCreate(BaseModel):
    meeting_id: int
    stage: DealStage = DealStage.INTRO
    notes: str = ""
    assigned_to: str = ""

class DealUpdateStage(BaseModel):
    stage: DealStage

@router.post("/", response_model=dict)
def create_deal(deal: DealCreate, db: Session = Depends(get_db)):
    meeting = db.query(Meeting).filter(Meeting.id == deal.meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    new_deal = Deal(
        meeting_id=deal.meeting_id,
        stage=deal.stage,
        notes=deal.notes,
        assigned_to=deal.assigned_to,
        assigned_at=datetime.utcnow()
    )
    db.add(new_deal)
    db.commit()
    db.refresh(new_deal)
    return {"id": new_deal.id, "message": "Deal created"}

@router.get("/", response_model=List[dict])
def list_deals(db: Session = Depends(get_db)):
    deals = db.query(Deal).all()
    return [
        {
            "id": d.id,
            "meeting_id": d.meeting_id,
            "stage": d.stage.value,
            "notes": d.notes,
            "assigned_to": d.assigned_to,
            "assigned_at": d.assigned_at.isoformat() if d.assigned_at else None,
        }
        for d in deals
    ]

@router.put("/{deal_id}/stage")
def update_deal_stage(deal_id: int, stage_update: DealUpdateStage, db: Session = Depends(get_db)):
    deal = db.query(Deal).filter(Deal.id == deal_id).first()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    deal.stage = stage_update.stage
    db.commit()
    return {"message": "Deal stage updated"}