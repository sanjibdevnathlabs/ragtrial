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
CONFIGURATION_LOADED = "configuration_loaded"
GEMINI_API_KEY_MISSING = "gemini_api_key_missing"
GOOGLE_API_CONFIGURED = "google_generative_ai_configured"
GOOGLE_API_CONFIG_FAILED = "google_api_configuration_failed"
SETUP_COMPLETE = "setup_complete"

# Ingestion messages
MSG_GEMINI_API_KEY_MISSING = "GEMINI_API_KEY not found in environment or config"
MSG_SETUP_COMPLETE = "Ready to load documents"
MSG_CONFIG_FILE_ENSURE = "Please ensure 'environment/default.toml' exists."

# ============================================================================
# VECTORSTORE TRACE CODES & MESSAGES
# ============================================================================
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
EMBEDDINGS_INITIALIZING = "embeddings_initializing"
EMBEDDINGS_INITIALIZED = "embeddings_initialized"
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

