# app/api/insurance.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import date

from ..models.insurance import Insurance, InsuranceCreate, InsuranceUpdate
from ..services.database import get_db
from ..services import kafka_producer

router = APIRouter(prefix="/insurance", tags=["insurance"])


@router.post("/", response_model=Insurance)
async def create_insurance(
        insurance: InsuranceCreate,
        db: Session = Depends(get_db)
):
    """Create a new insurance record"""
    db_insurance = Insurance(**insurance.dict())
    db.add(db_insurance)
    db.commit()
    db.refresh(db_insurance)

    # Send insurance event to Kafka
    await kafka_producer.send_insurance_event(
        "insurance-updates",
        {"type": "new_insurance", "insurance_id": db_insurance.insurance_id}
    )

    return db_insurance


@router.get("/{insurance_id}", response_model=Insurance)
async def get_insurance(insurance_id: int, db: Session = Depends(get_db)):
    """Get insurance details by ID"""
    insurance = db.query(Insurance).filter(Insurance.insurance_id == insurance_id).first()
    if not insurance:
        raise HTTPException(status_code=404, detail="Insurance not found")
    return insurance


@router.get("/patient/{patient_id}", response_model=List[Insurance])
async def list_patient_insurance(
        patient_id: int,
        active_only: bool = False,
        db: Session = Depends(get_db)
):
    """List all insurance records for a specific patient"""
    query = db.query(Insurance).filter(Insurance.patient_id == patient_id)

    if active_only:
        current_date = date.today()
        query = query.filter(
            Insurance.coverage_start_date <= current_date,
            Insurance.coverage_end_date >= current_date
        )

    return query.all()


@router.put("/{insurance_id}", response_model=Insurance)
async def update_insurance(
        insurance_id: int,
        insurance_update: InsuranceUpdate,
        db: Session = Depends(get_db)
):
    """Update insurance information"""
    db_insurance = db.query(Insurance).filter(Insurance.insurance_id == insurance_id).first()
    if not db_insurance:
        raise HTTPException(status_code=404, detail="Insurance not found")

    for field, value in insurance_update.dict(exclude_unset=True).items():
        setattr(db_insurance, field, value)

    db.commit()
    db.refresh(db_insurance)

    # Send insurance update event to Kafka
    await kafka_producer.send_insurance_event(
        "insurance-updates",
        {"type": "insurance_updated", "insurance_id": insurance_id}
    )

    return db_insurance


@router.delete("/{insurance_id}")
async def delete_insurance(insurance_id: int, db: Session = Depends(get_db)):
    """Delete an insurance record"""
    insurance = db.query(Insurance).filter(Insurance.insurance_id == insurance_id).first()
    if not insurance:
        raise HTTPException(status_code=404, detail="Insurance not found")

    db.delete(insurance)
    db.commit()

    # Send insurance deletion event to Kafka
    await kafka_producer.send_insurance_event(
        "insurance-updates",
        {"type": "insurance_deleted", "insurance_id": insurance_id}
    )

    return {"message": "Insurance record deleted successfully"}