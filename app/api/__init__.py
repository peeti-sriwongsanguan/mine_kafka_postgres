# app/api/__init__.py
from fastapi import APIRouter
from .patients import router as patients_router
from .treatments import router as treatments_router
from .insurance import router as insurance_router

router = APIRouter()

# Include all routers
router.include_router(patients_router)
router.include_router(treatments_router)
router.include_router(insurance_router)

# Health check endpoint
@router.get("/health")
async def health_check():
    return {"status": "healthy"}