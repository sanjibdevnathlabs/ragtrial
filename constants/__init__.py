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

