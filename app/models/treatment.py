# app/models/treatment.py
from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Numeric, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime

from ..services.database import Base

# SQLAlchemy Model
class Treatment(Base):
    __tablename__ = "treatments"

    treatment_id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.patient_id"), nullable=False)
    treatment_date = Column(Date, nullable=False)
    diagnosis = Column(Text, nullable=False)
    treatment_description = Column(Text, nullable=False)
    provider_notes = Column(Text)
    cost = Column(Numeric(10, 2), nullable=False)
    insurance_coverage = Column(Numeric(10, 2))
    patient_responsibility = Column(Numeric(10, 2))
    follow_up_date = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    patient = relationship("Patient", back_populates="treatments")
    images = relationship("PatientImage", back_populates="treatment")

    def __repr__(self):
        return f"<Treatment {self.treatment_id} for Patient {self.patient_id}>"

# SQLAlchemy Model for Patient Images
class PatientImage(Base):
    __tablename__ = "patient_images"

    image_id = Column(Integer, primary_key=True, index=True)
    treatment_id = Column(Integer, ForeignKey("treatments.treatment_id"), nullable=False)
    image_type = Column(String(20), nullable=False)  # 'before' or 'after'
    s3_key = Column(String(200), nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship
    treatment = relationship("Treatment", back_populates="images")

# Pydantic Models for API
class TreatmentBase(BaseModel):
    patient_id: int
    treatment_date: date
    diagnosis: str
    treatment_description: str
    provider_notes: Optional[str] = None
    cost: float
    insurance_coverage: Optional[float] = None
    patient_responsibility: Optional[float] = None
    follow_up_date: Optional[date] = None

class TreatmentCreate(TreatmentBase):
    pass

class TreatmentUpdate(BaseModel):
    treatment_date: Optional[date] = None
    diagnosis: Optional[str] = None
    treatment_description: Optional[str] = None
    provider_notes: Optional[str] = None
    cost: Optional[float] = None
    insurance_coverage: Optional[float] = None
    patient_responsibility: Optional[float] = None
    follow_up_date: Optional[date] = None

class PatientImageBase(BaseModel):
    treatment_id: int
    image_type: str
    s3_key: str

class PatientImageCreate(PatientImageBase):
    pass

class PatientImage(PatientImageBase):
    image_id: int
    uploaded_at: datetime

    class Config:
        orm_mode = True

class Treatment(TreatmentBase):
    treatment_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    images: List[PatientImage] = []

    class Config:
        orm_mode = True