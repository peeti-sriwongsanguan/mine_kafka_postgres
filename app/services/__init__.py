# app/services/__init__.py
from .database import get_db, init_db, drop_db
from .s3_service import S3Service
from .kafka_producer import KafkaProducerService
from .kafka_consumer import KafkaConsumerService

# Initialize services
s3_service = S3Service()
kafka_producer = KafkaProducerService()
kafka_consumer = KafkaConsumerService()

__all__ = [
    'get_db',
    'init_db',
    'drop_db',
    's3_service',
    'kafka_producer',
    'kafka_consumer'
]