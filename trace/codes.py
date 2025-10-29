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
API_ROUTES_REGISTERED = "api_routes_registered"
API_ROUTE_REGISTERED = "api_route_registered"
API_ROUTES_COUNT = "api_routes_count"

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

# ============================================================================
# DATABASE TRACE CODES & MESSAGES
# ============================================================================

# Connection trace codes
DB_CONNECTION_INITIALIZING = "db_connection_initializing"
DB_CONNECTION_ESTABLISHED = "db_connection_established"
DB_CONNECTION_FAILED = "db_connection_failed"
DB_CONNECTION_CLOSED = "db_connection_closed"
DB_CONNECTION_TIMEOUT = "db_connection_timeout"
DB_CONNECTION_POOL_CREATED = "db_connection_pool_created"
DB_CONNECTION_POOL_EXHAUSTED = "db_connection_pool_exhausted"

# Engine trace codes
DB_ENGINE_CREATING = "db_engine_creating"
DB_ENGINE_CREATED = "db_engine_created"
DB_ENGINE_INITIALIZING = "db_engine_initializing"
DB_ENGINE_INITIALIZED = "db_engine_initialized"
DB_ENGINE_DISPOSED = "db_engine_disposed"

# Session trace codes
DB_SESSION_CREATING = "db_session_creating"
DB_SESSION_CREATED = "db_session_created"
DB_SESSION_CLOSED = "db_session_closed"
DB_SESSION_ERROR = "db_session_error"
DB_SESSION_WRITE = "db_session_write"
DB_SESSION_READ = "db_session_read"

# Transaction trace codes
DB_TRANSACTION_STARTED = "db_transaction_started"
DB_TRANSACTION_COMMITTED = "db_transaction_committed"
DB_TRANSACTION_ROLLED_BACK = "db_transaction_rolled_back"
DB_TRANSACTION_FAILED = "db_transaction_failed"

# Query trace codes
DB_QUERY_STARTED = "db_query_started"
DB_QUERY_EXECUTED = "db_query_executed"
DB_QUERY_COMPLETED = "db_query_completed"
DB_QUERY_FAILED = "db_query_failed"
DB_QUERY_SLOW = "db_query_slow"
DB_QUERY_PARAMETERIZED = "db_query_parameterized"

# Repository trace codes
REPOSITORY_OPERATION_STARTED = "repository_operation_started"
REPOSITORY_OPERATION_COMPLETED = "repository_operation_completed"
REPOSITORY_OPERATION_FAILED = "repository_operation_failed"
REPOSITORY_ENTITY_CREATED = "repository_entity_created"
REPOSITORY_ENTITY_UPDATED = "repository_entity_updated"
REPOSITORY_ENTITY_DELETED = "repository_entity_deleted"
REPOSITORY_ENTITY_FOUND = "repository_entity_found"
REPOSITORY_ENTITY_NOT_FOUND = "repository_entity_not_found"
REPOSITORY_DUPLICATE_ENTRY = "repository_duplicate_entry"

# Database repository trace code aliases
DB_REPOSITORY_STARTED = "repository_operation_started"
DB_REPOSITORY_COMPLETED = "repository_operation_completed"
DB_REPOSITORY_FAILED = "repository_operation_failed"

# Migration trace codes
MIGRATION_SYSTEM_INITIALIZING = "migration_system_initializing"
MIGRATION_SYSTEM_INITIALIZED = "migration_system_initialized"
MIGRATION_CHECKING_STATUS = "migration_checking_status"
MIGRATION_STATUS_RETRIEVED = "migration_status_retrieved"
MIGRATION_GENERATING = "migration_generating"
MIGRATION_GENERATED = "migration_generated"
MIGRATION_APPLYING = "migration_applying"
MIGRATION_APPLIED = "migration_applied"
MIGRATION_ROLLING_BACK = "migration_rolling_back"
MIGRATION_ROLLED_BACK = "migration_rolled_back"
MIGRATION_FAILED = "migration_failed"
DB_MIGRATION_FAILED = "db_migration_failed"  # Alias for migration failures
MIGRATION_UP_STARTED = "migration_up_started"
MIGRATION_UP_COMPLETED = "migration_up_completed"
MIGRATION_DOWN_STARTED = "migration_down_started"
MIGRATION_DOWN_COMPLETED = "migration_down_completed"
MIGRATION_RESET_STARTED = "migration_reset_started"
MIGRATION_RESET_COMPLETED = "migration_reset_completed"
MIGRATION_ALREADY_APPLIED = "migration_already_applied"
MIGRATION_NOT_APPLIED = "migration_not_applied"
DB_MIGRATION_STATUS_CHECK = "db_migration_status_check"
DB_MIGRATION_STATUS = "db_migration_status"
DB_MIGRATION_PENDING = "db_migration_pending"
DB_MIGRATION_UP_STARTED = "db_migration_up_started"
DB_MIGRATION_UP_COMPLETED = "db_migration_up_completed"
DB_MIGRATION_DOWN_STARTED = "db_migration_down_started"
DB_MIGRATION_DOWN_COMPLETED = "db_migration_down_completed"
DB_MIGRATION_GENERATE = "db_migration_generate"

# Database initialization trace codes
DB_INITIALIZING = "db_initializing"
DB_INITIALIZED = "db_initialized"
DB_CREATING_TABLES = "db_creating_tables"
DB_TABLES_CREATED = "db_tables_created"
DB_SEEDING = "db_seeding"
DB_SEEDED = "db_seeded"
DB_MIGRATION_TABLE_EXISTS = "db_migration_table_exists"
DB_MIGRATION_TABLE_CREATED = "db_migration_table_created"
