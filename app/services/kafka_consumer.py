# app/services/kafka_consumer.py
import json
from kafka import KafkaConsumer
import os
from dotenv import load_dotenv
import logging
from typing import Callable, Dict, Any
import asyncio
from concurrent.futures import ThreadPoolExecutor

load_dotenv()

logger = logging.getLogger(__name__)

class KafkaConsumerService:
    def __init__(self):
        self.bootstrap_servers = os.getenv(
            "KAFKA_BOOTSTRAP_SERVERS",
            "localhost:9092"
        )
        self.consumers: Dict[str, KafkaConsumer] = {}
        self.executor = ThreadPoolExecutor(max_workers=5)
        self.running = False

    def create_consumer(self, topic: str, group_id: str) -> KafkaConsumer:
        """Create a new Kafka consumer for a topic"""
        try:
            consumer = KafkaConsumer(
                topic,
                bootstrap_servers=self.bootstrap_servers,
                group_id=group_id,
                auto_offset_reset='earliest',
                enable_auto_commit=True,
                value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                key_deserializer=lambda x: x.decode('utf-8') if x else None
            )
            return consumer
        except Exception as e:
            logger.error(f"Failed to create consumer for topic {topic}: {e}")
            raise

    def process_messages(self, consumer: KafkaConsumer, handler: Callable):
        """Process messages from a Kafka topic"""
        try:
            for message in consumer:
                if not self.running:
                    break
                try:
                    handler(message.value)
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
        except Exception as e:
            logger.error(f"Error in message processing loop: {e}")

    async def start_consuming(self, topic: str, group_id: str, handler: Callable):
        """Start consuming messages from a topic"""
        if topic in self.consumers:
            logger.warning(f"Consumer for topic {topic} already exists")
            return

        try:
            consumer = self.create_consumer(topic, group_id)
            self.consumers[topic] = consumer
            self.running = True

            # Run the consumer in a separate thread
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                self.executor,
                self.process_messages,
                consumer,
                handler
            )
        except Exception as e:
            logger.error(f"Failed to start consuming from topic {topic}: {e}")
            raise

    def stop_consuming(self, topic: str):
        """Stop consuming messages from a topic"""
        if topic in self.consumers:
            self.running = False
            consumer = self.consumers[topic]
            consumer.close()
            del self.consumers[topic]
            logger.info(f"Stopped consuming from topic {topic}")

    def close_all(self):
        """Close all consumers"""
        self.running = False
        for topic in list(self.consumers.keys()):
            self.stop_consuming(topic)
        self.executor.shutdown(wait=True)
        logger.info("All Kafka consumers closed")