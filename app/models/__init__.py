# app/models/__init__.py
from .patient import Patient, PatientCreate, PatientUpdate
from .treatment import Treatment, TreatmentCreate, TreatmentUpdate, PatientImage
from .insurance import Insurance, InsuranceCreate, InsuranceUpdate

# Import all models for database creation
__all__ = [
    "Patient",
    "PatientCreate",
    "PatientUpdate",
    "Treatment",
    "TreatmentCreate",
    "TreatmentUpdate",
    "PatientImage",
    "Insurance",
    "InsuranceCreate",
    "InsuranceUpdate"
]