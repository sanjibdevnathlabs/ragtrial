"""
Vector store configuration classes.

Contains configuration for Chroma, Pinecone, Qdrant, and Weaviate vector stores.
"""


class ChromaConfig:
    """ChromaDB-specific configuration"""

    persist_directory: str = "storage/chroma"
    distance_function: str = "cosine"
    anonymized_telemetry: bool = False


class PineconeConfig:
    """Pinecone-specific configuration"""

    api_key: str = None
    cloud: str = "aws"  # Cloud provider: aws, gcp, azure
    region: str = (
        "us-east-1"  # Cloud region (AWS: us-east-1, GCP: us-central1, Azure: eastus)
    )
    index_name: str = "rag-documents"
    dimension: int = 768
    metric: str = "cosine"  # Similarity metric: cosine, euclidean, dotproduct
    verify_ssl: bool = True  # SSL certificate verification (disable for dev if needed)


class QdrantConfig:
    """Qdrant-specific configuration"""

    host: str = "localhost"
    port: int = 6333
    grpc_port: int = 6334
    prefer_grpc: bool = False
    api_key: str = ""
    distance: str = "Cosine"


class WeaviateConfig:
    """Weaviate-specific configuration"""

    url: str = "http://localhost:8080"
    api_key: str = ""
    class_name: str = "RagDocument"
    distance: str = "cosine"
    grpc_port: int = 50051  # Default gRPC port (must differ from HTTP port)
    default_http_port: int = 8080  # Default HTTP port if not in URL
    default_https_port: int = 443  # Default HTTPS port if not in URL


class VectorStoreConfig:
    """Vector store configuration"""

    provider: str = "chroma"
    collection_name: str = "rag_documents"
    chroma: ChromaConfig = None
    pinecone: PineconeConfig = None
    qdrant: QdrantConfig = None
    weaviate: WeaviateConfig = None
