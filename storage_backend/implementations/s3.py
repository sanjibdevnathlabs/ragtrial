"""
AWS S3 Storage Implementation.

Supports:
- AWS S3 (production)
- LocalStack (local development)
- Secure credential discovery (IAM Role, IRSA, Environment variables)
"""

import os
from datetime import datetime
from io import BytesIO
from typing import BinaryIO, Dict, List, Optional

import boto3
from botocore.exceptions import ClientError, NoCredentialsError

import constants
from logger import get_logger
from trace import codes

logger = get_logger(__name__)


class S3Storage:
    """AWS S3 storage implementation.
    
    Features:
    - Automatic credential discovery (IAM Role, IRSA, Environment)
    - LocalStack support for development
    - Role assumption for cross-account access
    - Secure by default (no hardcoded credentials)
    """

    def __init__(self, config):
        """
        Initialize S3 storage with secure credential discovery.
        
        Args:
            config: Application configuration
        """
        logger.info(
            codes.STORAGE_INITIALIZING,
            backend=constants.STORAGE_BACKEND_S3
        )
        
        s3_config = config.storage.s3
        self.bucket_name = s3_config.bucket_name
        self.region = s3_config.region
        
        self.session = self._create_session(s3_config)
        self.client = self._create_client(s3_config)
        
        self._verify_bucket_access()
        
        logger.info(
            codes.STORAGE_INITIALIZED,
            backend=constants.STORAGE_BACKEND_S3,
            bucket=self.bucket_name,
            region=self.region,
            message=codes.MSG_STORAGE_INITIALIZED
        )

    def _create_session(self, s3_config) -> boto3.Session:
        """
        Create boto3 session with credential discovery.
        
        Credentials are discovered in this order:
        1. IAM Role (EC2/ECS/Lambda)
        2. IRSA (Kubernetes Service Account)
        3. Environment variables
        4. AWS CLI config
        5. Explicit credentials (LocalStack only)
        """
        if s3_config.role_arn:
            return self._create_assumed_role_session(s3_config)
        
        if not s3_config.use_explicit_credentials:
            logger.info(codes.STORAGE_CREDENTIALS_FOUND, method="credential_chain")
            return boto3.Session(region_name=s3_config.region)
        
        if s3_config.use_localstack:
            logger.warning("Using explicit credentials for LocalStack")
            return self._create_localstack_session(s3_config)
        
        return self._create_env_session(s3_config)

    def _create_assumed_role_session(self, s3_config) -> boto3.Session:
        """Create session by assuming IAM role."""
        logger.info(codes.STORAGE_USING_IAM_ROLE, role_arn=s3_config.role_arn)
        
        sts_client = boto3.client("sts", region_name=s3_config.region)
        
        response = sts_client.assume_role(
            RoleArn=s3_config.role_arn,
            RoleSessionName=s3_config.role_session_name or "rag-app-session",
            DurationSeconds=3600
        )
        
        credentials = response["Credentials"]
        
        return boto3.Session(
            aws_access_key_id=credentials["AccessKeyId"],
            aws_secret_access_key=credentials["SecretAccessKey"],
            aws_session_token=credentials["SessionToken"],
            region_name=s3_config.region
        )

    def _create_localstack_session(self, s3_config) -> boto3.Session:
        """Create session for LocalStack testing."""
        return boto3.Session(
            aws_access_key_id=s3_config.access_key_id or "test",
            aws_secret_access_key=s3_config.secret_access_key or "test",
            region_name=s3_config.region
        )

    def _create_env_session(self, s3_config) -> boto3.Session:
        """Create session from environment variables."""
        access_key = os.getenv("AWS_ACCESS_KEY_ID") or s3_config.access_key_id
        secret_key = os.getenv("AWS_SECRET_ACCESS_KEY") or s3_config.secret_access_key
        session_token = os.getenv("AWS_SESSION_TOKEN")
        
        if not access_key or not secret_key:
            logger.error(codes.STORAGE_ERROR, message=codes.MSG_STORAGE_NO_CREDENTIALS)
            raise ValueError(constants.ERROR_NO_AWS_CREDENTIALS)
        
        logger.info(codes.STORAGE_CREDENTIALS_FOUND, method=constants.S3_CREDENTIAL_METHOD_ENV_VARS)
        
        return boto3.Session(
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            aws_session_token=session_token,
            region_name=s3_config.region
        )

    def _create_client(self, s3_config):
        """Create S3 client with optional endpoint override."""
        client_kwargs = {"service_name": "s3", "region_name": s3_config.region}
        
        if s3_config.endpoint_url:
            client_kwargs["endpoint_url"] = s3_config.endpoint_url
            logger.info("Using custom S3 endpoint", endpoint=s3_config.endpoint_url)
        
        return self.session.client(**client_kwargs)

    def _verify_bucket_access(self) -> None:
        """Verify bucket access and log credential source."""
        self.client.head_bucket(Bucket=self.bucket_name)
        
        credentials = self.session.get_credentials()
        credential_method = credentials.method if credentials else "unknown"
        
        logger.info(
            codes.STORAGE_BUCKET_ACCESS_VERIFIED,
            bucket=self.bucket_name,
            credential_method=credential_method
        )

    def upload_file(self, file_stream: BinaryIO, filename: str) -> str:
        """
        Upload file to S3.
        
        Args:
            file_stream: Binary file stream
            filename: Target filename (S3 key)
            
        Returns:
            S3 key of uploaded file
        """
        logger.info(
            codes.STORAGE_UPLOADING,
            filename=filename,
            bucket=self.bucket_name
        )
        
        self.client.upload_fileobj(file_stream, self.bucket_name, filename)
        
        logger.info(
            codes.STORAGE_UPLOADED,
            filename=filename,
            bucket=self.bucket_name,
            message=codes.MSG_STORAGE_UPLOADED
        )
        
        return filename

    def download_file(self, filename: str) -> BinaryIO:
        """
        Download file from S3.
        
        Args:
            filename: S3 key to download
            
        Returns:
            Binary file stream
        """
        if not self.file_exists(filename):
            logger.error(codes.STORAGE_FILE_NOT_FOUND, filename=filename)
            raise FileNotFoundError(f"{constants.ERROR_FILE_NOT_FOUND_STORAGE}: {filename}")
        
        logger.info(codes.STORAGE_DOWNLOADING, filename=filename)
        
        stream = BytesIO()
        self.client.download_fileobj(self.bucket_name, filename, stream)
        stream.seek(0)
        
        logger.info(codes.STORAGE_DOWNLOADED, filename=filename, size=stream.getbuffer().nbytes)
        
        return stream

    def delete_file(self, filename: str) -> bool:
        """
        Delete file from S3.
        
        Args:
            filename: S3 key to delete
            
        Returns:
            True if deleted successfully
        """
        if not self.file_exists(filename):
            logger.warning(codes.STORAGE_FILE_NOT_FOUND, filename=filename)
            return False
        
        logger.info(codes.STORAGE_DELETING, filename=filename)
        
        self.client.delete_object(Bucket=self.bucket_name, Key=filename)
        
        logger.info(codes.STORAGE_DELETED, filename=filename, message=codes.MSG_STORAGE_DELETED)
        
        return True

    def list_files(self, prefix: str = "") -> List[str]:
        """
        List files in S3 bucket.
        
        Args:
            prefix: Optional prefix to filter files
            
        Returns:
            List of S3 keys
        """
        logger.info(codes.STORAGE_LISTING, prefix=prefix or "all")
        
        paginator = self.client.get_paginator("list_objects_v2")
        pages = paginator.paginate(Bucket=self.bucket_name, Prefix=prefix)
        
        files = []
        for page in pages:
            if "Contents" not in page:
                continue
            
            files.extend([obj["Key"] for obj in page["Contents"]])
        
        logger.info(codes.STORAGE_LISTED, count=len(files))
        
        return sorted(files)

    def file_exists(self, filename: str) -> bool:
        """
        Check if file exists in S3.
        
        Args:
            filename: S3 key to check
            
        Returns:
            True if file exists
        """
        try:
            self.client.head_object(Bucket=self.bucket_name, Key=filename)
            logger.debug(codes.STORAGE_FILE_EXISTS, filename=filename)
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return False
            raise

    def get_file_metadata(self, filename: str) -> Dict[str, str]:
        """
        Get file metadata from S3.
        
        Args:
            filename: S3 key
            
        Returns:
            Dictionary with metadata
        """
        if not self.file_exists(filename):
            logger.error(codes.STORAGE_FILE_NOT_FOUND, filename=filename)
            raise FileNotFoundError(f"{constants.ERROR_FILE_NOT_FOUND_STORAGE}: {filename}")
        
        response = self.client.head_object(Bucket=self.bucket_name, Key=filename)
        
        return {
            "filename": filename,
            "size": str(response["ContentLength"]),
            "modified_time": response["LastModified"].isoformat(),
            "etag": response["ETag"].strip('"')
        }

