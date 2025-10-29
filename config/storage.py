"""
Storage backend configuration classes.

Contains configuration for local and S3 storage backends.
"""


class LocalStorageConfig:
    """Local storage-specific configuration"""

    path: str = "source_docs"
    create_if_missing: bool = True


class S3StorageConfig:
    """S3 storage-specific configuration"""

    bucket_name: str = "rag-documents"
    region: str = "us-east-1"
    use_explicit_credentials: bool = False
    access_key_id: str = ""
    secret_access_key: str = ""
    endpoint_url: str = ""
    use_localstack: bool = False
    role_arn: str = ""
    role_session_name: str = "rag-app"


class StorageConfig:
    """Storage backend configuration"""

    backend: str = "local"
    max_file_size_mb: int = 100
    allowed_extensions: list = None
    local: LocalStorageConfig = None
    s3: S3StorageConfig = None
