# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import router as api_router
from .services.database import init_db

app = FastAPI(
    title="Healthcare POS API",
    description="API for Healthcare Point of Service System",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database tables
init_db()

# Include routers
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Healthcare POS API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}