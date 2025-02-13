# app/services/s3_service.py
import boto3
import os
from dotenv import load_dotenv
from datetime import datetime
import logging
from botocore.exceptions import ClientError
from typing import Optional, BinaryIO

load_dotenv()

logger = logging.getLogger(__name__)


class S3Service:
    def __init__(self):
        self.aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
        self.aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        self.region_name = os.getenv('AWS_REGION', 'us-east-1')
        self.bucket_name = os.getenv('AWS_BUCKET_NAME', 'mine-pos')

        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            region_name=self.region_name
        )

        # Define standard paths
        self.paths = {
            'patient_images': 'healthcare/patient_images',
            'documents': 'healthcare/documents',
            'backups': 'healthcare/backups/database',
            'audit_logs': 'healthcare/audit_logs'
        }

    async def upload_file(
            self,
            file_obj: BinaryIO,
            folder: str,
            filename: str,
            content_type: Optional[str] = None
    ) -> str:
        """Upload a file to S3"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            key = f"{folder}/{timestamp}_{filename}"

            extra_args = {
                'ServerSideEncryption': 'AES256'
            }
            if content_type:
                extra_args['ContentType'] = content_type

            self.s3_client.upload_fileobj(
                file_obj,
                self.bucket_name,
                key,
                ExtraArgs=extra_args
            )

            logger.info(f"File uploaded successfully: {key}")
            return key
        except Exception as e:
            logger.error(f"Error uploading file to S3: {e}")
            raise

    async def download_file(self, key: str) -> bytes:
        """Download a file from S3"""
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=key
            )
            return response['Body'].read()
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                logger.error(f"File not found in S3: {key}")
                return None
            raise
        except Exception as e:
            logger.error(f"Error downloading file from S3: {e}")
            raise

    async def store_patient_image(
            self,
            patient_id: int,
            image_file: BinaryIO,
            image_type: str
    ) -> str:
        """Store a patient image"""
        folder = f"{self.paths['patient_images']}/{patient_id}"
        filename = f"{image_type}.jpg"
        return await self.upload_file(
            image_file,
            folder,
            filename,
            'image/jpeg'
        )

    async def store_document(
            self,
            patient_id: int,
            document_file: BinaryIO,
            document_type: str,
            file_extension: str
    ) -> str:
        """Store a patient document"""
        folder = f"{self.paths['documents']}/{patient_id}"
        filename = f"{document_type}.{file_extension}"
        return await self.upload_file(
            document_file,
            folder,
            filename
        )

    async def backup_database(self, backup_file: BinaryIO) -> str:
        """Store a database backup"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"backup_{timestamp}.sql"
        return await self.upload_file(
            backup_file,
            self.paths['backups'],
            filename
        )

    async def delete_file(self, key: str):
        """Delete a file from S3"""
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=key
            )
            logger.info(f"File deleted successfully: {key}")
        except Exception as e:
            logger.error(f"Error deleting file from S3: {e}")
            raise

    def generate_presigned_url(self, key: str, expiration: int = 3600) -> str:
        """Generate a presigned URL for a file"""
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': key
                },
                ExpiresIn=expiration
            )
            return url
        except Exception as e:
            logger.error(f"Error generating presigned URL: {e}")
            raise