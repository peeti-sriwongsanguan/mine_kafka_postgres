# app/services/kafka_producer.py
import json
import os
from dotenv import load_dotenv
from typing import Any, Dict, Optional
import logging
from kafka import KafkaProducer
from kafka.errors import KafkaError
import time

load_dotenv()

logger = logging.getLogger(__name__)


class KafkaProducerService:
    def __init__(self):
        self.bootstrap_servers = 'localhost:9092'  # Use external port
        self.producer = None
        self.max_retries = 3
        self.retry_interval = 2  # seconds
        self.initialize_producer()

    def initialize_producer(self) -> None:
        """Initialize the Kafka producer with retries"""
        retries = 0
        while retries < self.max_retries:
            try:
                self.producer = KafkaProducer(
                    bootstrap_servers=self.bootstrap_servers,
                    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                    key_serializer=lambda k: k.encode('utf-8') if k else None,
                    api_version=(2, 5, 0),
                    acks='all',
                    retries=3,
                    retry_backoff_ms=1000,
                    request_timeout_ms=5000,
                    max_block_ms=5000
                )
                logger.info(f"Kafka producer initialized successfully with bootstrap servers: {self.bootstrap_servers}")
                return
            except KafkaError as e:
                retries += 1
                logger.warning(f"Failed to initialize Kafka producer (attempt {retries}/{self.max_retries}): {e}")
                if retries < self.max_retries:
                    time.sleep(self.retry_interval)
                else:
                    logger.error("Failed to initialize Kafka producer after all retries")
                    self.producer = None

    async def send_event(self, topic: str, event: Dict[str, Any], key: Optional[str] = None) -> bool:
        """Send an event to a Kafka topic"""
        if not self.producer:
            logger.warning(f"Kafka producer not available, skipping event: {event}")
            return False

        try:
            future = self.producer.send(topic, value=event, key=key)
            record_metadata = future.get(timeout=10)
            logger.info(f"Event sent to topic {topic}: {event}")
            logger.debug(
                f"Message delivered to partition {record_metadata.partition} with offset {record_metadata.offset}")
            return True
        except Exception as e:
            logger.error(f"Failed to send event to topic {topic}: {e}")
            return False

    async def send_patient_event(self, topic: str, event: Dict[str, Any]) -> bool:
        """Send a patient-related event"""
        event['event_type'] = 'patient'
        return await self.send_event(topic, event)

    async def send_treatment_event(self, topic: str, event: Dict[str, Any]) -> bool:
        """Send a treatment-related event"""
        event['event_type'] = 'treatment'
        return await self.send_event(topic, event)

    async def send_insurance_event(self, topic: str, event: Dict[str, Any]) -> bool:
        """Send an insurance-related event"""
        event['event_type'] = 'insurance'
        return await self.send_event(topic, event)

    def close(self) -> None:
        """Close the Kafka producer"""
        if self.producer:
            self.producer.close(timeout=5)
            logger.info("Kafka producer closed")