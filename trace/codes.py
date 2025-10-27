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

