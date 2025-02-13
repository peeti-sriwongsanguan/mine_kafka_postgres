# app/api/treatments.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import date

from ..models.treatment import Treatment, TreatmentCreate, TreatmentUpdate
from ..services.database import get_db
from ..services import kafka_producer

router = APIRouter(prefix="/treatments", tags=["treatments"])


@router.post("/", response_model=Treatment)
async def create_treatment(
        treatment: TreatmentCreate,
        db: Session = Depends(get_db)
):
    """Create a new treatment record"""
    db_treatment = Treatment(**treatment.dict())
    db.add(db_treatment)
    db.commit()
    db.refresh(db_treatment)

    # Send treatment event to Kafka
    await kafka_producer.send_treatment_event(
        "treatment-events",
        {"type": "new_treatment", "treatment_id": db_treatment.treatment_id}
    )

    return db_treatment


@router.get("/{treatment_id}", response_model=Treatment)
async def get_treatment(treatment_id: int, db: Session = Depends(get_db)):
    """Get treatment details by ID"""
    treatment = db.query(Treatment).filter(Treatment.treatment_id == treatment_id).first()
    if not treatment:
        raise HTTPException(status_code=404, detail="Treatment not found")
    return treatment


@router.get("/patient/{patient_id}", response_model=List[Treatment])
async def list_patient_treatments(
        patient_id: int,
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db)
):
    """List all treatments for a specific patient"""
    treatments = db.query(Treatment) \
        .filter(Treatment.patient_id == patient_id) \
        .offset(skip) \
        .limit(limit) \
        .all()
    return treatments


@router.put("/{treatment_id}", response_model=Treatment)
async def update_treatment(
        treatment_id: int,
        treatment_update: TreatmentUpdate,
        db: Session = Depends(get_db)
):
    """Update treatment information"""
    db_treatment = db.query(Treatment).filter(Treatment.treatment_id == treatment_id).first()
    if not db_treatment:
        raise HTTPException(status_code=404, detail="Treatment not found")

    for field, value in treatment_update.dict(exclude_unset=True).items():
        setattr(db_treatment, field, value)

    db.commit()
    db.refresh(db_treatment)

    # Send treatment update event to Kafka
    await kafka_producer.send_treatment_event(
        "treatment-events",
        {"type": "treatment_updated", "treatment_id": treatment_id}
    )

    return db_treatment


@router.delete("/{treatment_id}")
async def delete_treatment(treatment_id: int, db: Session = Depends(get_db)):
    """Delete a treatment record"""
    treatment = db.query(Treatment).filter(Treatment.treatment_id == treatment_id).first()
    if not treatment:
        raise HTTPException(status_code=404, detail="Treatment not found")

    db.delete(treatment)
    db.commit()

    # Send treatment deletion event to Kafka
    await kafka_producer.send_treatment_event(
        "treatment-events",
        {"type": "treatment_deleted", "treatment_id": treatment_id}
    )

    return {"message": "Treatment deleted successfully"}