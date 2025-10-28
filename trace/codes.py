"""
All trace codes and messages in one place.

This module contains ALL trace codes (event names) and messages used
throughout the application. NO string literals should be used in the code.

All constants use UPPER_SNAKE_CASE naming convention.
"""

# ============================================================================
# COMMON TRACE CODES
# ============================================================================

# App lifecycle
EVENT_APP_STARTED = "app_started"
EVENT_APP_SHUTDOWN = "app_shutdown"
SCRIPT_STARTED = "script_started"
SCRIPT_COMPLETED = "script_completed"
SCRIPT_EXIT_SUCCESS = "script_exit_success"
SCRIPT_EXIT_ERROR = "script_exit_error"

# Operation trace codes
OPERATION_CLEAR = "operation_clear"

# Demo trace codes
DEMO_STARTED = "demo_started"
DEMO_COMPLETED = "demo_completed"
DEMO_QUERY_STARTED = "demo_query_started"
DEMO_INSTRUCTIONS = "demo_instructions"

# General operations
OPERATION_FAILED = "operation_failed"
VALIDATION_ERROR = "validation_error"

# Setup/Test operations
PREREQUISITES_CHECKING = "prerequisites_checking"
PREREQUISITES_PASSED = "prerequisites_passed"
PREREQUISITES_FAILED = "prerequisites_failed"
PYTHON_VERSION_CHECK = "python_version_check"
FILE_CHECK = "file_check"
ENV_VAR_CHECK = "env_var_check"
DIRECTORY_CREATING = "directory_creating"
DIRECTORY_CREATED = "directory_created"
TEST_STARTING = "test_starting"
TEST_PASSED = "test_passed"
TEST_FAILED = "test_failed"


# ============================================================================
# CONFIG TRACE CODES & MESSAGES
# ============================================================================

# Config trace codes
CONFIG_LOADING = "config_loading"
CONFIG_LOADED = "config_loaded"
CONFIG_LOADING_OVERRIDE = "config_loading_override"
CONFIG_FILE_NOT_FOUND = "config_file_not_found"
CONFIG_LOAD_FAILED = "config_load_failed"
CONFIG_WARNING = "config_warning"
CONFIG_WARNING_APP_ENV_NOT_FOUND = "config_warning_app_env_not_found"

# Config messages
MSG_CONFIG_LOADED = "Config loaded successfully"
MSG_CONFIG_FILE_NOT_FOUND = "Configuration file not found"
MSG_APP_NAME_MISSING = "app.name was not found in any config file"
MSG_GOOGLE_API_KEY_MISSING = "google.api_key was not found in any config file"
MSG_LOADING_OVERRIDE_CONFIG = "Loading override config"
MSG_WARNING_PREFIX = "Warning"


# ============================================================================
# INGESTION TRACE CODES & MESSAGES
# ============================================================================

# Ingestion trace codes
INGESTION_SCRIPT_STARTED = "ingestion_script_started"
INGESTION_SCANNING_DIRECTORY = "ingestion_scanning_directory"
INGESTION_FILES_FOUND = "ingestion_files_found"
INGESTION_PROCESSING_FILE = "ingestion_processing_file"
INGESTION_FILE_LOADED = "ingestion_file_loaded"
INGESTION_FILE_SPLIT = "ingestion_file_split"
INGESTION_FILE_EMBEDDED = "ingestion_file_embedded"
INGESTION_FILE_STORED = "ingestion_file_stored"
INGESTION_FILE_SUCCESS = "ingestion_file_success"
INGESTION_FILE_SKIPPED = "ingestion_file_skipped"
INGESTION_FILE_ERROR = "ingestion_file_error"
INGESTION_COMPLETE = "ingestion_complete"
INGESTION_CLEARING_VECTORSTORE = "ingestion_clearing_vectorstore"
INGESTION_VECTORSTORE_CLEARED = "ingestion_vectorstore_cleared"

CONFIGURATION_LOADED = "configuration_loaded"
GEMINI_API_KEY_MISSING = "gemini_api_key_missing"
GOOGLE_API_CONFIGURED = "google_generative_ai_configured"
GOOGLE_API_CONFIG_FAILED = "google_api_configuration_failed"
SETUP_COMPLETE = "setup_complete"

# Ingestion messages
MSG_GEMINI_API_KEY_MISSING = "GEMINI_API_KEY not found in environment or config"
MSG_SETUP_COMPLETE = "Ready to load documents"
MSG_CONFIG_FILE_ENSURE = "Please ensure 'environment/default.toml' exists."
MSG_NO_FILES_FOUND = "No supported files found in directory"
MSG_INGESTION_SUMMARY = "Ingestion complete"

# ============================================================================
# VECTORSTORE TRACE CODES & MESSAGES
# ============================================================================
VECTORSTORE_CREATING = "vectorstore_creating"
VECTORSTORE_INITIALIZING = "vectorstore_initializing"
VECTORSTORE_INITIALIZED = "vectorstore_initialized"
VECTORSTORE_FACTORY_CREATING = "vectorstore_factory_creating"
VECTORSTORE_COLLECTION_CREATING = "vectorstore_collection_creating"
VECTORSTORE_COLLECTION_CREATED = "vectorstore_collection_created"
VECTORSTORE_COLLECTION_EXISTS = "vectorstore_collection_exists"
VECTORSTORE_DOCUMENTS_ADDING = "vectorstore_documents_adding"
VECTORSTORE_DOCUMENTS_ADDED = "vectorstore_documents_added"
VECTORSTORE_QUERYING = "vectorstore_querying"
VECTORSTORE_QUERY_RESULTS = "vectorstore_query_results"
VECTORSTORE_DELETING = "vectorstore_deleting"
VECTORSTORE_DELETED = "vectorstore_deleted"
VECTORSTORE_STATS = "vectorstore_stats"
VECTORSTORE_ERROR = "vectorstore_error"
VECTORSTORE_PROVIDER_UNKNOWN = "vectorstore_provider_unknown"

MSG_VECTORSTORE_INITIALIZED = "Vector store initialized successfully"
MSG_VECTORSTORE_COLLECTION_CREATED = "Collection created successfully"
MSG_VECTORSTORE_COLLECTION_EXISTS = "Collection already exists"
MSG_VECTORSTORE_DOCUMENTS_ADDED = "Documents added successfully"
MSG_VECTORSTORE_PROVIDER_UNKNOWN = "Unknown vectorstore provider"

# ============================================================================
# EMBEDDINGS TRACE CODES & MESSAGES
# ============================================================================
EMBEDDINGS_CREATING = "embeddings_creating"
EMBEDDINGS_INITIALIZING = "embeddings_initializing"
EMBEDDINGS_INITIALIZED = "embeddings_initialized"
EMBEDDINGS_MODEL_LOADING = "embeddings_model_loading"
EMBEDDINGS_FACTORY_CREATING = "embeddings_factory_creating"
EMBEDDINGS_GENERATING = "embeddings_generating"
EMBEDDINGS_GENERATED = "embeddings_generated"
EMBEDDINGS_BATCH_PROCESSING = "embeddings_batch_processing"
EMBEDDINGS_BATCH_COMPLETE = "embeddings_batch_complete"
EMBEDDINGS_ERROR = "embeddings_error"
EMBEDDINGS_PROVIDER_UNKNOWN = "embeddings_provider_unknown"

MSG_EMBEDDINGS_INITIALIZED = "Embeddings initialized successfully"
MSG_EMBEDDINGS_GENERATED = "Embeddings generated successfully"
MSG_EMBEDDINGS_PROVIDER_UNKNOWN = "Unknown embeddings provider"

# ============================================================================
# DOCUMENT LOADING TRACE CODES & MESSAGES
# ============================================================================

# Document loader trace codes
LOADER_INITIALIZING = "loader_initializing"
LOADER_INITIALIZED = "loader_initialized"
LOADER_LOADING_FILE = "loader_loading_file"
LOADER_FILE_LOADED = "loader_file_loaded"
LOADER_FILE_NOT_FOUND = "loader_file_not_found"
LOADER_UNSUPPORTED_FORMAT = "loader_unsupported_format"
LOADER_LOADING_ERROR = "loader_loading_error"
LOADER_EMPTY_DOCUMENT = "loader_empty_document"
LOADER_DETECTING_TYPE = "loader_detecting_type"
LOADER_TYPE_DETECTED = "loader_type_detected"

# Document loader messages
MSG_LOADER_INITIALIZED = "Document loader initialized"
MSG_LOADER_LOADING_FILE = "Loading document from file"
MSG_LOADER_FILE_LOADED = "Document loaded successfully"
MSG_LOADER_FILE_NOT_FOUND = "File not found"
MSG_LOADER_UNSUPPORTED_FORMAT = "Unsupported file format"
MSG_LOADER_LOADING_ERROR = "Error loading document"
MSG_LOADER_EMPTY_DOCUMENT = "Document has no content"
MSG_LOADER_DETECTING_TYPE = "Detecting file type"
MSG_LOADER_TYPE_DETECTED = "File type detected"

# ============================================================================
# TEXT SPLITTING TRACE CODES & MESSAGES
# ============================================================================

# Text splitter trace codes
SPLITTER_INITIALIZING = "splitter_initializing"
SPLITTER_INITIALIZED = "splitter_initialized"
SPLITTER_SPLITTING = "splitter_splitting"
SPLITTER_SPLIT_COMPLETE = "splitter_split_complete"
SPLITTER_INVALID_PARAMS = "splitter_invalid_params"
SPLITTER_EMPTY_TEXT = "splitter_empty_text"
SPLITTER_ERROR = "splitter_error"

# Text splitter messages
MSG_SPLITTER_INITIALIZED = "Text splitter initialized"
MSG_SPLITTER_SPLITTING = "Splitting documents into chunks"
MSG_SPLITTER_SPLIT_COMPLETE = "Documents split successfully"
MSG_SPLITTER_INVALID_PARAMS = "Invalid splitting parameters"
MSG_SPLITTER_EMPTY_TEXT = "No text to split"
MSG_SPLITTER_ERROR = "Error splitting documents"

# ============================================================================
# STORAGE BACKEND TRACE CODES & MESSAGES
# ============================================================================

# Storage trace codes
STORAGE_INITIALIZING = "storage_initializing"
STORAGE_INITIALIZED = "storage_initialized"
STORAGE_UPLOADING = "storage_uploading"
STORAGE_UPLOADED = "storage_uploaded"
STORAGE_DOWNLOADING = "storage_downloading"
STORAGE_DOWNLOADED = "storage_downloaded"
STORAGE_DELETING = "storage_deleting"
STORAGE_DELETED = "storage_deleted"
STORAGE_LISTING = "storage_listing"
STORAGE_LISTED = "storage_listed"
STORAGE_FILE_EXISTS = "storage_file_exists"
STORAGE_FILE_NOT_FOUND = "storage_file_not_found"
STORAGE_ERROR = "storage_error"
STORAGE_CREDENTIALS_FOUND = "storage_credentials_found"
STORAGE_USING_IAM_ROLE = "storage_using_iam_role"
STORAGE_USING_IRSA = "storage_using_irsa"
STORAGE_BUCKET_ACCESS_VERIFIED = "storage_bucket_access_verified"

# Storage messages
MSG_STORAGE_INITIALIZED = "Storage backend initialized successfully"
MSG_STORAGE_UPLOADED = "File uploaded successfully"
MSG_STORAGE_DOWNLOADED = "File downloaded successfully"
MSG_STORAGE_DELETED = "File deleted successfully"
MSG_STORAGE_FILE_EXISTS = "File exists in storage"
MSG_STORAGE_FILE_NOT_FOUND = "File not found in storage"
MSG_STORAGE_ERROR = "Storage operation failed"
MSG_STORAGE_NO_CREDENTIALS = "No AWS credentials found"
MSG_STORAGE_BUCKET_ACCESS_DENIED = "Access denied to S3 bucket"

# ============================================================================
# API TRACE CODES & MESSAGES
# ============================================================================

# API trace codes
API_SERVER_STARTING = "api_server_starting"
API_SERVER_STARTED = "api_server_started"
API_SERVER_SHUTDOWN = "api_server_shutdown"
API_REQUEST_RECEIVED = "api_request_received"
API_REQUEST_COMPLETED = "api_request_completed"
API_HEALTH_CHECK_REQUESTED = "api_health_check_requested"
API_UPLOAD_STARTED = "api_upload_started"
API_UPLOAD_COMPLETED = "api_upload_completed"
API_UPLOAD_FAILED = "api_upload_failed"
API_FILE_TOO_LARGE = "api_file_too_large"
API_INVALID_FILE_TYPE = "api_invalid_file_type"
API_FILE_DELETED = "api_file_deleted"
API_FILE_NOT_FOUND = "api_file_not_found"
API_FILES_LISTED = "api_files_listed"
API_FILE_METADATA_RETRIEVED = "api_file_metadata_retrieved"
API_VALIDATION_ERROR = "api_validation_error"
API_ERROR = "api_error"

# API messages
MSG_API_SERVER_STARTED = "API server started successfully"
MSG_API_SERVER_SHUTDOWN = "API server shutdown initiated"
MSG_API_UPLOAD_COMPLETED = "File upload completed"
MSG_API_UPLOAD_FAILED = "File upload failed"
MSG_API_FILE_TOO_LARGE = "File size exceeds maximum allowed"
MSG_API_INVALID_FILE_TYPE = "File type not supported"
MSG_API_FILE_DELETED = "File deleted successfully"
MSG_API_FILE_NOT_FOUND = "File not found"
MSG_API_FILES_LISTED = "Files listed successfully"
MSG_API_ERROR = "An error occurred processing the request"

# Storage dependency trace codes
STORAGE_DEPENDENCY_INJECTING = "storage_dependency_injecting"
STORAGE_DEPENDENCY_RELEASED = "storage_dependency_released"
STORAGE_FACTORY_CREATING = "storage_factory_creating"

# ============================================================================
# RAG (RETRIEVAL-AUGMENTED GENERATION) TRACE CODES & MESSAGES
# ============================================================================
RAG_CHAIN_INITIALIZING = "rag_chain_initializing"
RAG_CHAIN_INITIALIZED = "rag_chain_initialized"
RAG_CHAIN_INIT_FAILED = "rag_chain_init_failed"
RAG_CHAIN_NOT_INITIALIZED = "rag_chain_not_initialized"
RAG_QUERY_RECEIVED = "rag_query_received"
RAG_QUERY_PROCESSING = "rag_query_processing"
RAG_RETRIEVAL_STARTED = "rag_retrieval_started"
RAG_RETRIEVAL_COMPLETED = "rag_retrieval_completed"
RAG_RETRIEVAL_FAILED = "rag_retrieval_failed"
RAG_NO_DOCUMENTS_FOUND = "rag_no_documents_found"
RAG_LLM_GENERATING = "rag_llm_generating"
RAG_LLM_GENERATED = "rag_llm_generated"
RAG_LLM_FAILED = "rag_llm_failed"
RAG_RESPONSE_FORMATTED = "rag_response_formatted"
RAG_QUERY_COMPLETED = "rag_query_completed"
RAG_QUERY_FAILED = "rag_query_failed"

# RAG messages (imported from constants)
from constants import (
    MSG_RAG_CHAIN_INITIALIZED,
    MSG_RAG_QUERY_PROCESSING,
    MSG_RAG_QUERY_COMPLETED,
    MSG_RAG_NO_RELEVANT_DOCS,
    MSG_RAG_INSUFFICIENT_CONTEXT,
    ERROR_RAG_CHAIN_INIT_FAILED,
    ERROR_RAG_QUERY_FAILED,
    ERROR_RAG_RETRIEVAL_FAILED,
    ERROR_RAG_LLM_FAILED,
    ERROR_RAG_INVALID_QUERY,
)


# ============================================================================
# API QUERY TRACE CODES & MESSAGES
# ============================================================================
QUERY_SERVICE_INITIALIZING = "query_service_initializing"
QUERY_SERVICE_INITIALIZED = "query_service_initialized"
QUERY_API_REQUEST_RECEIVED = "query_api_request_received"
QUERY_API_VALIDATION_FAILED = "query_api_validation_failed"
QUERY_API_PROCESSING = "query_api_processing"
QUERY_API_COMPLETED = "query_api_completed"
QUERY_API_FAILED = "query_api_failed"

# Query messages (imported from constants)
from constants import (
    MSG_QUERY_RECEIVED,
    MSG_QUERY_PROCESSING,
    MSG_QUERY_COMPLETED,
    MSG_QUERY_SERVICE_INITIALIZED,
    ERROR_QUERY_EMPTY,
    ERROR_QUERY_TOO_SHORT,
    ERROR_QUERY_PROCESSING_FAILED,
    ERROR_RAG_CHAIN_NOT_INITIALIZED,
    ERROR_RAG_CHAIN_INITIALIZATION_FAILED,
)


# ============================================================================
# SECURITY GUARDRAILS TRACE CODES & MESSAGES
# ============================================================================
GUARDRAILS_INITIALIZING = "guardrails_initializing"
GUARDRAILS_INITIALIZED = "guardrails_initialized"
INPUT_VALIDATION_STARTED = "input_validation_started"
INPUT_VALIDATION_PASSED = "input_validation_passed"
INPUT_VALIDATION_FAILED = "input_validation_failed"
INJECTION_DETECTION_STARTED = "injection_detection_started"
INJECTION_DETECTION_PASSED = "injection_detection_passed"
INJECTION_DETECTED = "injection_detected"
OUTPUT_VALIDATION_STARTED = "output_validation_started"
OUTPUT_VALIDATION_PASSED = "output_validation_passed"
OUTPUT_VALIDATION_FAILED = "output_validation_failed"
SECURITY_VIOLATION_DETECTED = "security_violation_detected"
QUERY_BLOCKED_BY_GUARDRAILS = "query_blocked_by_guardrails"
OUTPUT_BLOCKED_BY_GUARDRAILS = "output_blocked_by_guardrails"

# Security messages (imported from constants)
from constants import (
    MSG_GUARDRAILS_INITIALIZED,
    MSG_INPUT_VALIDATION_PASSED,
    MSG_NO_INJECTION_DETECTED,
    MSG_OUTPUT_VALIDATION_PASSED,
    MSG_SECURITY_VIOLATIONS_DETECTED,
    MSG_OUTPUT_VIOLATIONS_DETECTED,
    MSG_QUERY_BLOCKED,
    MSG_LLM_OUTPUT_BLOCKED,
    ERROR_INVALID_INPUT,
    ERROR_PROMPT_INJECTION,
    ERROR_UNSAFE_OUTPUT,
    ERROR_BLOCKED_BY_GUARDRAILS,
    ERROR_OUTPUT_BLOCKED,
)

