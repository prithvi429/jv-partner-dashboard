from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import models
from database import get_db

from pydantic import BaseModel

router = APIRouter()

class DealCreate(BaseModel):
    name: str
    company_name: str
    product_name: str
    value: float = 0.0

class DealRead(BaseModel):
    id: int
    name: str
    company_name: str
    product_name: str
    value: float

    class Config:
        orm_mode = True

@router.post("/", response_model=DealRead)
def create_deal(payload: DealCreate, db: Session = Depends(get_db)):
    # get or create company
    company = db.query(models.Company).filter_by(name=payload.company_name).first()
    if not company:
        company = models.Company(name=payload.company_name)
        db.add(company)
        db.flush()

    product = db.query(models.Product).filter_by(name=payload.product_name).first()
    if not product:
        product = models.Product(name=payload.product_name)
        db.add(product)
        db.flush()

    deal = models.Deal(name=payload.name, company=company, product=product, value=payload.value)
    db.add(deal)
    db.commit()
    db.refresh(deal)

    return {
        "id": deal.id,
        "name": deal.name,
        "company_name": company.name,
        "product_name": product.name,
        "value": deal.value,
    }

@router.get("/", response_model=List[DealRead])
def list_deals(db: Session = Depends(get_db)):
    deals = db.query(models.Deal).all()
    result = []
    for d in deals:
        result.append({
            "id": d.id,
            "name": d.name,
            "company_name": d.company.name,
            "product_name": d.product.name,
            "value": d.value,
        })
    return result
