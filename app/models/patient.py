# app/models/patient.py
from sqlalchemy import Column, Integer, String, Date, Enum, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, List
from datetime import date, datetime
from enum import Enum as PyEnum

from ..services.database import Base


class Gender(str, PyEnum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class MaritalStatus(str, PyEnum):
    SINGLE = "single"
    MARRIED = "married"
    DIVORCED = "divorced"
    WIDOWED = "widowed"


# SQLAlchemy Model
class Patient(Base):
    __tablename__ = "patients"

    patient_id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(Enum(Gender), nullable=False)
    marital_status = Column(Enum(MaritalStatus))
    race = Column(String(50))
    occupation = Column(String(100))
    email = Column(String(100), unique=True)
    phone = Column(String(20))
    address = Column(String(200))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    treatments = relationship("Treatment", back_populates="patient")
    insurance_records = relationship("Insurance", back_populates="patient")

    def __repr__(self):
        return f"<Patient {self.first_name} {self.last_name}>"


# Pydantic Models for API
class PatientBase(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: date
    gender: Gender
    marital_status: Optional[MaritalStatus] = None
    race: Optional[str] = None
    occupation: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class PatientCreate(PatientBase):
    pass


class PatientUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[Gender] = None
    marital_status: Optional[MaritalStatus] = None
    race: Optional[str] = None
    occupation: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class PatientInDB(PatientBase):
    patient_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)