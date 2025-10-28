"""
Application Constants - All non-logging string literals.

This module contains all string constants used throughout the application
that are NOT trace codes for logging (those go in trace/codes.py).

All constants use UPPER_SNAKE_CASE naming convention.

Usage:
    import constants
    
    logger.info(codes.SCRIPT_STARTED, header=constants.SETUP_HEADER)
"""

# ============================================================================
# SETUP SCRIPT CONSTANTS
# ============================================================================

# Headers
SETUP_HEADER = "RAG Application - Database Setup"
SETUP_COMPLETE_HEADER = "DATABASE SETUP COMPLETE!"
QUICK_TEST_HEADER = "Quick Test - Local Setup (No API)"
QUICK_TEST_COMPLETE = "LOCAL SETUP TEST PASSED!"

# Prerequisites
CHECK_PREREQUISITES = "Checking prerequisites..."
PYTHON_VERSION_NEED_MIN = "need 3.9+"

# Configuration
LOADING_CONFIGURATION = "Loading configuration..."
CONFIGURATION_LOADED = "Configuration loaded"
CONFIG_APP_LABEL = "App"
CONFIG_VECTORSTORE_LABEL = "Vectorstore"
CONFIG_EMBEDDINGS_LABEL = "Embeddings"

# Directory creation
CREATING_DIRECTORIES = "Creating storage directories..."

# Embeddings testing
TESTING_EMBEDDINGS = "Testing embeddings provider..."
EMBEDDINGS_PROVIDER_LABEL = "Provider"
EMBEDDINGS_MODEL_LABEL = "Model"
EMBEDDINGS_API_WAIT = "Calling API (this may take 5-10 seconds)..."
GENERATING_EMBEDDING = "Generating embedding..."
EMPTY_EMBEDDING_RETURNED = "Failed: Empty embedding returned"

# Vectorstore testing
TESTING_VECTORSTORE = "Testing vectorstore..."
VECTORSTORE_PROVIDER_LABEL = "Provider"
VECTORSTORE_STORAGE_LABEL = "Storage"
COLLECTION_INITIALIZED = "Collection initialized"
TEST_DOCUMENT_ADDED = "Test document added"
NO_QUERY_RESULTS = "Failed: No results from query"

# ChromaDB testing
CHROMADB_CLIENT_CREATED = "ChromaDB client created"
COLLECTION_CLEANED_UP = "Test collection cleaned up"

# Test data
TEST_DOCUMENT_TEXT = "This is a test document for the RAG system."
TEST_DOCUMENT_SOURCE = "setup_test"
TEST_DOCUMENT_TYPE = "test"
TEST_QUERY_TEXT = "test document"
TEST_SENTENCE = "This is a test sentence."
TEST_COLLECTION_NAME = "test_collection"
TEST_COLLECTION_METADATA_KEY = "test"
TEST_COLLECTION_METADATA_VALUE = "true"
TEST_SOURCE_LABEL = "source"

# Summary
SUMMARY_HEADER = "Summary:"

# Next steps
NEXT_STEPS_HEADER = "Next Steps:"
NEXT_STEP_PLACE_DOCUMENTS = "1. Place documents in source_docs/ folder"
NEXT_STEP_RUN_INGESTION = "2. Run: python ingestion/ingest.py"
NEXT_STEP_TRY_EXAMPLES = "3. Or try examples:"
EXAMPLE_DEMO_VECTORSTORE = "   • python examples/demo_vectorstore.py"
EXAMPLE_DEMO_PROVIDER_SWITCHING = "   • python examples/demo_provider_switching.py"

# Provider switching
SWITCH_PROVIDERS_TIP = "To switch providers:"
SWITCH_PROVIDERS_EDIT_CONFIG = "   • Edit environment/default.toml"
SWITCH_PROVIDERS_CHANGE_SETTING = "   • Change [vectorstore] provider = '...'"
SWITCH_PROVIDERS_SEE_DOCS = "   • See docs/PROVIDERS.md for all options"

# ============================================================================
# INGESTION CONSTANTS
# ============================================================================

# Directories
SOURCE_DOCS_DIR = "source_docs"
DEFAULT_SOURCE_DIR = "source_docs"

# Progress messages
INGESTION_HEADER = "Document Ingestion Pipeline"
SCANNING_FOR_FILES = "Scanning for documents..."
FOUND_FILES_TEMPLATE = "Found {count} files"
PROCESSING_FILE_TEMPLATE = "Processing {current}/{total}: {filename}"
FILE_SUCCESS_TEMPLATE = "✓ {filename}"
FILE_ERROR_TEMPLATE = "✗ {filename}: {error}"
FILE_SKIPPED_TEMPLATE = "⊘ {filename}: {reason}"

# Summary labels
INGESTION_SUMMARY_HEADER = "Ingestion Summary"
SUMMARY_TOTAL_FILES = "Total files"
SUMMARY_SUCCESSFUL = "Successful"
SUMMARY_FAILED = "Failed"
SUMMARY_SKIPPED = "Skipped"
SUMMARY_TOTAL_CHUNKS = "Total chunks created"
SUMMARY_DURATION = "Duration"

# Error messages
ERROR_NO_FILES_FOUND = "No supported files found in directory"
ERROR_DIRECTORY_NOT_FOUND = "Source directory not found"
ERROR_FILE_PROCESSING_FAILED = "Failed to process file"

# ============================================================================
# STORAGE BACKEND CONSTANTS
# ============================================================================

# Storage backends
STORAGE_BACKEND_LOCAL = "local"
STORAGE_BACKEND_S3 = "s3"

# Storage operations
OPERATION_UPLOAD = "upload"
OPERATION_DOWNLOAD = "download"
OPERATION_DELETE = "delete"
OPERATION_LIST = "list"
OPERATION_EXISTS = "exists"

# Local storage
DEFAULT_LOCAL_STORAGE_PATH = "source_docs"

# S3 storage
DEFAULT_S3_REGION = "us-east-1"
S3_CREDENTIAL_METHOD_IAM_ROLE = "IAM Role"
S3_CREDENTIAL_METHOD_IRSA = "IRSA"
S3_CREDENTIAL_METHOD_ENV_VARS = "Environment Variables"
S3_CREDENTIAL_METHOD_EXPLICIT = "Explicit Credentials"

# Storage errors
ERROR_STORAGE_NOT_INITIALIZED = "Storage backend not initialized"
ERROR_FILE_NOT_FOUND_STORAGE = "File not found in storage"
ERROR_UPLOAD_FAILED = "File upload failed"
ERROR_DOWNLOAD_FAILED = "File download failed"
ERROR_DELETE_FAILED = "File deletion failed"
ERROR_INVALID_STORAGE_BACKEND = "Invalid storage backend"
ERROR_NO_AWS_CREDENTIALS = "No AWS credentials found"
ERROR_BUCKET_NOT_FOUND = "S3 bucket not found"
ERROR_BUCKET_ACCESS_DENIED = "Access denied to S3 bucket"

# ============================================================================
# API CONSTANTS
# ============================================================================

# API settings
DEFAULT_API_HOST = "0.0.0.0"
DEFAULT_API_PORT = 8000
DEFAULT_UPLOAD_CHUNK_SIZE = 1048576  # 1MB
DEFAULT_MAX_FILE_SIZE_MB = 100

# HTTP status messages
HTTP_STATUS_OK = "OK"
HTTP_STATUS_CREATED = "Created"
HTTP_STATUS_BAD_REQUEST = "Bad Request"
HTTP_STATUS_NOT_FOUND = "Not Found"
HTTP_STATUS_INTERNAL_ERROR = "Internal Server Error"

# API errors
ERROR_FILE_TOO_LARGE = "File size exceeds maximum allowed"
ERROR_INVALID_FILE_TYPE = "File type not allowed"
ERROR_NO_FILE_PROVIDED = "No file provided"
ERROR_UPLOAD_FAILED_API = "File upload failed"

# API success messages
SUCCESS_FILE_UPLOADED = "File uploaded successfully"
SUCCESS_FILE_DELETED = "File deleted successfully"
SUCCESS_FILES_LISTED = "Files listed successfully"

# Next step instructions (quick test)
NEXT_STEP_API_TEST = "Next Step: Test with API"
API_TEST_COMMAND = "   Run: python scripts/setup_database.py"
API_TEST_WILL_TEST = "   This will test:"
API_TEST_FEATURE_EMBEDDINGS = "   • Google Embeddings API (requires GEMINI_API_KEY)"
API_TEST_FEATURE_VECTORSTORE = "   • Full vectorstore integration"

# Troubleshooting
TROUBLESHOOT_API_HANG = "If API test hangs:"
TROUBLESHOOT_CHECK_NETWORK = "   • Check network connectivity"
TROUBLESHOOT_VERIFY_KEY = "   • Verify GEMINI_API_KEY is correct"
TROUBLESHOOT_CURL_TEST = "   • Try: curl https://generativelanguage.googleapis.com"

# ============================================================================
# ERROR/WARNING MESSAGES
# ============================================================================

# Environment warnings
VENV_WARNING = "Warning: Not running in a virtual environment!"
VENV_RECOMMENDATION = "Recommended: source venv/bin/activate"

# API key messages
GEMINI_KEY_NOT_SET = "GEMINI_API_KEY not set (required for embeddings)"
GEMINI_KEY_SET_COMMAND = "Run: export GEMINI_API_KEY='your-key'"
API_KEY_GET_INSTRUCTIONS = "Get your key from: https://aistudio.google.com/apikey"
API_KEY_STATUS_LABEL = "API Key set"
API_KEY_STATUS_YES = "Yes"
API_KEY_STATUS_NO = "No"
API_KEY_SET_ERROR = "Set it with: export GEMINI_API_KEY='your-key'"

# Error messages
PREREQUISITES_NOT_MET = "Prerequisites not met. Please fix the issues above."
FAILED_TO_LOAD_CONFIG = "Failed to load configuration"
FAILED_TO_CREATE_DIRECTORIES = "Failed to create directories"
EMBEDDINGS_TEST_FAILED = "Embeddings test failed. Cannot proceed."
VECTORSTORE_TEST_FAILED = "Vectorstore test failed."
UNEXPECTED_ERROR = "Unexpected error"

# Timeout/network errors
API_TIMEOUT_HELP = "The API call timed out. This could be:"
API_TIMEOUT_NETWORK = "   • Network connectivity issue"
API_TIMEOUT_SERVICE = "   • Google API service is slow/down"
API_TIMEOUT_FIREWALL = "   • Firewall blocking the request"

# API key errors
API_KEY_ERROR_HELP = "It looks like your API key is not set."

# ============================================================================
# FILE/DIRECTORY PATHS
# ============================================================================

ERROR_LOADING_CONFIGURATION = "Error loading configuration"
CONFIG_FILE_PATH = "environment/default.toml"
CONFIG_MODULE_PATH = "config/__init__.py"
EMBEDDINGS_MODULE_PATH = "embeddings/__init__.py"
VECTORSTORE_MODULE_PATH = "vectorstore/__init__.py"

# Storage directories
STORAGE_DIR_QDRANT = "storage/qdrant"
STORAGE_DIR_WEAVIATE = "storage/weaviate"
STORAGE_DIR_SOURCE_DOCS = "source_docs"

# ============================================================================
# API TEST CONSTANTS
# ============================================================================

API_TEST_WAIT = "Testing Google API (may take 5-10 seconds)..."
API_TEST_CONTENT = "test"
API_MODEL_NAME = "models/text-embedding-004"
API_TASK_TYPE = "retrieval_document"

# ============================================================================
# ENV VARIABLE NAMES
# ============================================================================

ENV_GEMINI_API_KEY = "GEMINI_API_KEY"

# ============================================================================
# STEP LABELS
# ============================================================================

STEP_1_LABEL = "1️⃣"
STEP_2_LABEL = "2️⃣"
STEP_3_LABEL = "3️⃣"
STEP_4_LABEL = "4️⃣"

STEP_1_DESCRIPTION = "Checking Python version..."
STEP_2_DESCRIPTION = "Loading configuration..."
STEP_3_DESCRIPTION = "Creating storage directories..."
STEP_4_DESCRIPTION = "Testing ChromaDB (local)..."

# ============================================================================
# STATUS INDICATORS
# ============================================================================

STATUS_SUCCESS = "✅"
STATUS_FAILURE = "❌"
STATUS_WARNING = "⚠️"
STATUS_INFO = "💡"
STATUS_WORKING = "⏳"

# ============================================================================
# SEPARATORS/FORMATTING
# ============================================================================

SEPARATOR_HEAVY = "=" * 70
SEPARATOR_LIGHT = "-" * 70
INDENT_1 = "   "
INDENT_2 = "      "

# ============================================================================
# SCRIPT EXIT MESSAGES
# ============================================================================

SCRIPT_EXIT_SUCCESS = 0
SCRIPT_EXIT_ERROR = 1
SCRIPT_EXIT_INTERRUPTED = 1

# ============================================================================
# DEMO SCRIPT CONSTANTS (demo_vectorstore.py)
# ============================================================================

DEMO_HEADER = "=== Vectorstore Demo ==="
DEMO_CREATING_EMBEDDINGS = "Creating embeddings provider"
DEMO_CREATING_VECTORSTORE = "Creating vectorstore"
DEMO_INITIALIZING = "Initializing vectorstore..."
DEMO_ADDING_DOCUMENTS = "Adding sample documents..."
DEMO_QUERYING_HEADER = "\n=== Querying ==="
DEMO_QUERY_PREFIX = "Query"
DEMO_FOUND_RESULTS = "Found {} results:"
DEMO_RESULT_PREFIX = "\n--- Result {} ---"
DEMO_TEXT_PREFIX = "Text"
DEMO_METADATA_PREFIX = "Metadata"
DEMO_DISTANCE_PREFIX = "Distance"
DEMO_FILTER_HEADER = "\n=== Querying with filter ==="
DEMO_FILTER_PREFIX = "Filter"
DEMO_COMPLETE = "\n=== Demo Complete ==="
DEMO_SWITCH_PROVIDERS = "\nTo switch providers:"
DEMO_SWITCH_STEP_1 = "1. Edit environment/default.toml"
DEMO_SWITCH_STEP_2 = "2. Change [vectorstore] provider = 'pinecone'"
DEMO_SWITCH_STEP_3 = "3. Run this script again - NO CODE CHANGES!"

# Sample demo data
DEMO_DOC_RAG = "RAG stands for Retrieval-Augmented Generation, a technique for improving LLM responses."
DEMO_DOC_VECTOR_DB = "Vector databases store embeddings for efficient similarity search."
DEMO_DOC_CHROMA = "ChromaDB is a popular open-source vector database for AI applications."
DEMO_DOC_LANGCHAIN = "LangChain provides abstractions for building LLM applications."
DEMO_DOC_PYTHON = "Python is a great language for data science and machine learning."

# Demo metadata sources
DEMO_SOURCE_RAG = "rag_intro.txt"
DEMO_SOURCE_VECTOR_DB = "vector_db.txt"
DEMO_SOURCE_CHROMA = "chroma.txt"
DEMO_SOURCE_LANGCHAIN = "langchain.txt"
DEMO_SOURCE_PYTHON = "python.txt"

# Demo metadata topics
DEMO_TOPIC_RAG = "RAG"
DEMO_TOPIC_DATABASES = "databases"
DEMO_TOPIC_FRAMEWORKS = "frameworks"
DEMO_TOPIC_PROGRAMMING = "programming"

# Demo queries
DEMO_QUERY_RAG = "What is RAG and how does it work?"
DEMO_QUERY_DATABASES = "Tell me about databases"

# ============================================================================
# CLEANUP SCRIPT CONSTANTS (cleanup_all_databases.py)
# ============================================================================

CLEANUP_HEADER = "🧹 CLEANING ALL VECTOR DATABASES"
CLEANUP_CLEANING_PREFIX = "\n📦 Cleaning {}..."
CLEANUP_BEFORE_PREFIX = "  Before: {} documents"
CLEANUP_NO_DOCUMENTS = "  ℹ️  No documents to clean"
CLEANUP_ALREADY_CLEAN = "  ✅ {} is already clean!"
CLEANUP_AFTER_PREFIX = "  After: {} documents"
CLEANUP_SUCCESS = "  ✅ {} cleaned successfully!"
CLEANUP_FAILED = "  ❌ Failed to clean {}: {}"
CLEANUP_COMPLETE = "✅ CLEANUP COMPLETE FOR ALL DATABASES!"
CLEANUP_RETRIEVING_NAMESPACES = "  📋 Retrieving all namespaces from Pinecone..."
CLEANUP_FOUND_NAMESPACES = "  📁 Found {} namespace(s): {}"
CLEANUP_DELETING_NAMESPACE = "  🗑️  Deleting all vectors from namespace '{}'..."
CLEANUP_DELETING_DEFAULT = "  🗑️  Deleting all vectors from default namespace..."
CLEANUP_WAITING_PROPAGATION = "  ⏳ Waiting 3 seconds for Pinecone deletion to propagate..."

# Cleanup provider list
CLEANUP_PROVIDERS = ["chroma", "qdrant", "weaviate", "pinecone"]

# ============================================================================
# POPULATE SCRIPT CONSTANTS (populate_sample_data.py)
# ============================================================================

POPULATE_HEADER_PREFIX = "Populating {} with sample data"
POPULATE_ADDING_PREFIX = "Adding {} sample documents to {}..."
POPULATE_SUCCESS_PREFIX = "✅ Successfully added {} documents to {}"
POPULATE_TESTING_QUERY = "Testing query..."
POPULATE_QUERY_RETURNED = "Query returned {} result(s)"
POPULATE_COMPLETE_PREFIX = "✅ {} POPULATED SUCCESSFULLY"
POPULATE_FAILED_PREFIX = "❌ Failed to populate {}"
POPULATE_SUMMARY_HEADER = "POPULATION SUMMARY"
POPULATE_STATUS_SUCCESS = "✅ SUCCESS"
POPULATE_STATUS_FAILED = "❌ FAILED"

# Populate test query
POPULATE_TEST_QUERY = "What is RAG and how does it work?"

# Populate databases message
POPULATE_DATABASES_PREFIX = "Populating databases: {}"

# ============================================================================
# SAMPLE DOCUMENTS FOR POPULATION
# ============================================================================

SAMPLE_DOC_AI_OVERVIEW = (
    "Artificial Intelligence is transforming the world through machine learning, "
    "natural language processing, and computer vision. AI systems can learn from "
    "data, recognize patterns, and make decisions with minimal human intervention."
)

SAMPLE_DOC_ML_BASICS = (
    "Machine Learning is a subset of AI that focuses on algorithms that improve "
    "through experience. It includes supervised learning, unsupervised learning, "
    "and reinforcement learning techniques."
)

SAMPLE_DOC_NLP = (
    "Natural Language Processing enables computers to understand, interpret, and "
    "generate human language. Applications include chatbots, translation, "
    "sentiment analysis, and text summarization."
)

SAMPLE_DOC_CV = (
    "Computer Vision allows machines to interpret and understand visual information "
    "from the world. It powers facial recognition, autonomous vehicles, medical "
    "image analysis, and augmented reality."
)

SAMPLE_DOC_DL = (
    "Deep Learning uses neural networks with multiple layers to learn complex "
    "patterns from large amounts of data. It has achieved breakthrough results "
    "in image recognition, speech processing, and game playing."
)

SAMPLE_DOC_RAG = (
    "Retrieval-Augmented Generation (RAG) combines retrieval systems with large "
    "language models to provide accurate, up-to-date responses grounded in "
    "external knowledge. RAG systems retrieve relevant documents and use them "
    "to generate contextually accurate answers."
)

SAMPLE_DOC_EMBEDDINGS = (
    "Vector embeddings represent text, images, or other data as dense numerical "
    "vectors in high-dimensional space. Similar items have similar embeddings, "
    "enabling semantic search and similarity matching."
)

SAMPLE_DOC_VECTORDB = (
    "Vector databases store and efficiently search high-dimensional vector embeddings. "
    "They enable fast semantic search, recommendation systems, and similarity "
    "matching at scale using algorithms like HNSW and IVF."
)

# Sample document metadata
SAMPLE_SOURCE_AI = "AI Textbook"
SAMPLE_SOURCE_ML = "ML Guide"
SAMPLE_SOURCE_NLP = "NLP Handbook"
SAMPLE_SOURCE_CV = "CV Research Paper"
SAMPLE_SOURCE_DL = "DL Tutorial"
SAMPLE_SOURCE_RAG = "RAG Paper 2024"
SAMPLE_SOURCE_EMBEDDINGS = "Embeddings Guide"
SAMPLE_SOURCE_VECTORDB = "VectorDB Overview"

SAMPLE_CATEGORY_OVERVIEW = "overview"
SAMPLE_CATEGORY_FUNDAMENTALS = "fundamentals"
SAMPLE_CATEGORY_APPLICATIONS = "applications"
SAMPLE_CATEGORY_ADVANCED = "advanced"
SAMPLE_CATEGORY_INFRASTRUCTURE = "infrastructure"

SAMPLE_TOPIC_AI = "artificial_intelligence"
SAMPLE_TOPIC_ML = "machine_learning"
SAMPLE_TOPIC_NLP = "nlp"
SAMPLE_TOPIC_CV = "computer_vision"
SAMPLE_TOPIC_DL = "deep_learning"
SAMPLE_TOPIC_RAG = "rag"
SAMPLE_TOPIC_EMBEDDINGS = "embeddings"
SAMPLE_TOPIC_VECTORDB = "vector_databases"

# ============================================================================
# SECURITY CONSTANTS
# ============================================================================

# Sensitive fields that should never be logged in full
SENSITIVE_FIELDS = [
    "api_key",
    "password",
    "secret",
    "token",
    "auth",
    "credential",
    "private_key",
    "access_key",
    "secret_key",
]

# Masking patterns
MASK_PREFIX = "****..."
MASK_SUFFIX_LENGTH = 4  # Show last 4 characters
MASK_MIN_LENGTH = 8  # Only mask if value is at least this long
MASK_NONE_VALUE = "****...None"
MASK_SHORT_VALUE = "****"

# Embeddings API response keys
EMBEDDING_KEY = "embedding"
TASK_TYPE_QUERY = "retrieval_query"
TASK_TYPE_DOCUMENT = "retrieval_document"

# Embeddings error messages
ERROR_OPENAI_NOT_INSTALLED = "openai package not installed. Run: pip install openai"
ERROR_SENTENCE_TRANSFORMERS_NOT_INSTALLED = "sentence-transformers package not installed. Run: pip install sentence-transformers"
ERROR_VOYAGEAI_NOT_INSTALLED = "voyageai package not installed. Run: pip install voyageai"
MSG_SSL_CERTIFI_BUNDLE = "Using certifi certificate bundle for SSL verification"
MSG_SSL_DISABLED_DEV = "SSL verification disabled for OpenAI API (development only)"
MSG_SSL_DISABLED_VOYAGEAI_DEV = "SSL verification disabled for Voyage AI API (development only)"

# Vectorstore error messages
ERROR_COLLECTION_NOT_INITIALIZED = "Collection not initialized. Call initialize() first."
ERROR_INDEX_NOT_INITIALIZED = "Index not initialized. Call initialize() first."
ERROR_PINECONE_NOT_INSTALLED = "pinecone package not installed. Run: pip install pinecone"
ERROR_QDRANT_NOT_INSTALLED = "qdrant-client package not installed. Run: pip install qdrant-client"
ERROR_WEAVIATE_NOT_INSTALLED = "weaviate-client package not installed. Run: pip install weaviate-client"
MSG_SSL_DISABLED_PINECONE_DEV = "⚠️  SSL verification disabled - DEVELOPMENT ONLY, NOT FOR PRODUCTION"

# Vectorstore operation names
OPERATION_ADD_DOCUMENTS = "add_documents"
OPERATION_QUERY = "query"
OPERATION_DELETE = "delete"
OPERATION_CLEAR = "clear"
OPERATION_CLEAR_ALL = "CLEAR ALL"
OPERATION_INITIALIZE = "initialize"
OPERATION_GET_STATS = "get_stats"

# ChromaDB metadata keys
CHROMA_HNSW_SPACE = "hnsw:space"

# Result dictionary keys
RESULT_KEY_ID = "id"
RESULT_KEY_TEXT = "text"
RESULT_KEY_METADATA = "metadata"
RESULT_KEY_DISTANCE = "distance"

# Stats dictionary keys
STATS_KEY_COLLECTION_NAME = "collection_name"
STATS_KEY_INDEX_NAME = "index_name"
STATS_KEY_COUNT = "count"
STATS_KEY_INITIALIZED = "initialized"
STATS_KEY_PERSIST_DIR = "persist_directory"
STATS_KEY_DISTANCE_FUNCTION = "distance_function"
STATS_KEY_DIMENSION = "dimension"
STATS_KEY_METRIC = "metric"
STATS_KEY_VECTORS_COUNT = "vectors_count"
STATS_KEY_INDEXED_VECTORS_COUNT = "indexed_vectors_count"

# Pinecone metadata keys
PINECONE_METADATA_TEXT = "text"

# Pinecone vector dict keys
PINECONE_VECTOR_ID = "id"
PINECONE_VECTOR_VALUES = "values"
PINECONE_VECTOR_METADATA = "metadata"

# Qdrant payload keys
QDRANT_PAYLOAD_TEXT = "text"

# Weaviate property keys
WEAVIATE_PROPERTY_TEXT = "text"
WEAVIATE_PROPERTY_METADATA = "metadata"

# URL protocol strings
URL_HTTP_PREFIX = "http://"
URL_HTTPS_PREFIX = "https://"
URL_HTTPS = "https"
URL_COLON = ":"

# ============================================================================
# DOCUMENT LOADING CONSTANTS
# ============================================================================

# Supported file extensions
EXT_PDF = ".pdf"
EXT_TXT = ".txt"
EXT_MD = ".md"
EXT_DOCX = ".docx"
EXT_CSV = ".csv"
EXT_JSON = ".json"

# File type identifiers
FILE_TYPE_PDF = "pdf"
FILE_TYPE_TXT = "text"
FILE_TYPE_MD = "markdown"
FILE_TYPE_DOCX = "docx"
FILE_TYPE_CSV = "csv"
FILE_TYPE_JSON = "json"
FILE_TYPE_UNKNOWN = "unknown"

# Document metadata keys
META_SOURCE = "source"
META_FILE_TYPE = "file_type"
META_FILE_SIZE = "file_size_bytes"

# Error messages for document loading
ERROR_FILE_NOT_FOUND = "File not found"
ERROR_FILE_NOT_EXISTS = "File does not exist"
ERROR_UNSUPPORTED_FORMAT = "Unsupported file format"
ERROR_FILE_CORRUPTED = "File appears to be corrupted or unreadable"
ERROR_LOADING_FAILED = "Failed to load document"
ERROR_EMPTY_DOCUMENT = "Document is empty or has no content"

# ============================================================================
# TEXT SPLITTING CONSTANTS
# ============================================================================

# Splitter types
SPLITTER_TYPE_TOKEN = "token"
SPLITTER_TYPE_RECURSIVE = "recursive"
SPLITTER_TYPE_CHARACTER = "character"

# Default splitting parameters
DEFAULT_CHUNK_SIZE = 512
DEFAULT_CHUNK_OVERLAP = 100

# Error messages for text splitting
ERROR_INVALID_CHUNK_SIZE = "Chunk size must be positive"
ERROR_INVALID_OVERLAP = "Overlap must be non-negative and less than chunk size"
ERROR_EMPTY_TEXT = "Text is empty, nothing to split"
ERROR_SPLITTING_FAILED = "Failed to split text"

