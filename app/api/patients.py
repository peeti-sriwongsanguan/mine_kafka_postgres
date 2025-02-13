# app/api/patients.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from ..models.patient import Patient, PatientCreate, PatientUpdate, PatientInDB
from ..services.database import get_db
from ..services.s3_service import S3Service

router = APIRouter(prefix="/patients", tags=["patients"])
s3_service = S3Service()


@router.post("/", response_model=PatientInDB)
async def create_patient(patient: PatientCreate, db: Session = Depends(get_db)):
    """Create a new patient record"""
    db_patient = Patient(**patient.dict())
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient


@router.get("/{patient_id}", response_model=PatientInDB)
async def get_patient(patient_id: int, db: Session = Depends(get_db)):
    """Get patient details by ID"""
    patient = db.query(Patient).filter(Patient.patient_id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


@router.get("/", response_model=List[PatientInDB])
async def list_patients(
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        db: Session = Depends(get_db)
):
    """List all patients with optional search"""
    query = db.query(Patient)
    if search:
        query = query.filter(
            Patient.first_name.ilike(f"%{search}%") |
            Patient.last_name.ilike(f"%{search}%")
        )
    return query.offset(skip).limit(limit).all()


@router.put("/{patient_id}", response_model=PatientInDB)
async def update_patient(
        patient_id: int,
        patient_update: PatientUpdate,
        db: Session = Depends(get_db)
):
    """Update patient information"""
    db_patient = db.query(Patient).filter(Patient.patient_id == patient_id).first()
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    for field, value in patient_update.dict(exclude_unset=True).items():
        setattr(db_patient, field, value)

    db.commit()
    db.refresh(db_patient)
    return db_patient


@router.post("/{patient_id}/images")
async def upload_patient_image(
        patient_id: int,
        image_type: str,
        file: UploadFile = File(...),
        db: Session = Depends(get_db)
):
    """Upload patient before/after images"""
    if image_type not in ["before", "after"]:
        raise HTTPException(status_code=400, detail="Image type must be 'before' or 'after'")

    patient = db.query(Patient).filter(Patient.patient_id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    image_key = await s3_service.store_patient_image(
        patient_id=patient_id,
        image_file=file.file,
        image_type=image_type
    )

    return {"message": "Image uploaded successfully", "image_key": image_key}


@router.delete("/{patient_id}")
async def delete_patient(patient_id: int, db: Session = Depends(get_db)):
    """Delete a patient record"""
    patient = db.query(Patient).filter(Patient.patient_id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    db.delete(patient)
    db.commit()
    return {"message": "Patient deleted successfully"}