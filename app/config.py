# app/config.py
from dotenv import load_dotenv
import os

load_dotenv()

# AWS Configuration
AWS_REGION = os.getenv('AWS_REGION')
AWS_BUCKET_NAME = os.getenv('AWS_BUCKET_NAME')
AWS_BUCKET_ARN = os.getenv('AWS_BUCKET_ARN')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")

# Kafka configuration
KAFKA_BOOTSTRAP_SERVERS = os.getenv(
    "KAFKA_BOOTSTRAP_SERVERS",
    "localhost:9092"
)