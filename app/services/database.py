# app/services/database.py
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

load_dotenv()

# Get database connection details from environment variables
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "healthcare_db")

# First connect to default 'postgres' database to create our db if needed
default_engine = create_engine(
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/postgres"
)


def ensure_database_exists():
    """Ensure the database exists, create it if it doesn't"""
    try:
        # Check if database exists
        with default_engine.connect() as conn:
            result = conn.execute(text(
                f"SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}'"
            )).scalar()

            if not result:
                # Database doesn't exist, create it
                # Close existing connections to postgres db first
                conn.execute(text("COMMIT"))
                conn.execute(text(f"CREATE DATABASE {DB_NAME}"))
                logger.info(f"Created database {DB_NAME}")
            else:
                logger.info(f"Database {DB_NAME} already exists")
    except Exception as e:
        logger.error(f"Error ensuring database exists: {e}")
        raise


# Create database URL for our app database
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,
    echo=True  # Set to False in production
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()


# Dependency for FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Initialize database
def init_db():
    """Initialize the database"""
    logger.info("Initializing database...")
    try:
        # Ensure database exists
        ensure_database_exists()

        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise


# Drop database
def drop_db():
    """Drop all tables"""
    Base.metadata.drop_all(bind=engine)