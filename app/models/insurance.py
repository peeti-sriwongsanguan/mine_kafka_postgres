# app/models/insurance.py
from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

from ..services.database import Base

# SQLAlchemy Model
class Insurance(Base):
    __tablename__ = "insurance"

    insurance_id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.patient_id"), nullable=False)
    provider_name = Column(String(100), nullable=False)
    policy_number = Column(String(50), nullable=False)
    group_number = Column(String(50))
    subscriber_name = Column(String(100))
    subscriber_relationship = Column(String(50))
    coverage_start_date = Column(Date, nullable=False)
    coverage_end_date = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    patient = relationship("Patient", back_populates="insurance_records")

    def __repr__(self):
        return f"<Insurance {self.provider_name} for Patient {self.patient_id}>"

# Pydantic Models for API
class InsuranceBase(BaseModel):
    patient_id: int
    provider_name: str
    policy_number: str
    group_number: Optional[str] = None
    subscriber_name: Optional[str] = None
    subscriber_relationship: Optional[str] = None
    coverage_start_date: date
    coverage_end_date: Optional[date] = None

class InsuranceCreate(InsuranceBase):
    pass

class InsuranceUpdate(BaseModel):
    provider_name: Optional[str] = None
    policy_number: Optional[str] = None
    group_number: Optional[str] = None
    subscriber_name: Optional[str] = None
    subscriber_relationship: Optional[str] = None
    coverage_start_date: Optional[date] = None
    coverage_end_date: Optional[date] = None

class Insurance(InsuranceBase):
    insurance_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True