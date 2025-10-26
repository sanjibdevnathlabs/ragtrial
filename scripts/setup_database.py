#!/usr/bin/env python3
"""
Database Setup Script for RAG Application

This script:
1. Creates necessary storage directories
2. Initializes ChromaDB (default local vectorstore)
3. Tests embeddings connection
4. Verifies the complete pipeline works

Run this script to set up your local database for the first time.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import Config
from embeddings import create_embeddings
from vectorstore import create_vectorstore
from logger import setup_logging, get_logger
from trace import codes
import constants

# Initialize logger early (before setup_logging)
logger = get_logger(__name__)


def create_storage_directories(config: Config, logger) -> None:
    """Create necessary storage directories."""
    logger.info(codes.DIRECTORY_CREATING, message=constants.CREATING_DIRECTORIES)
    
    # ChromaDB storage
    chroma_dir = Path(config.vectorstore.chroma.persist_directory)
    chroma_dir.mkdir(parents=True, exist_ok=True)
    logger.info(codes.DIRECTORY_CREATED, path=str(chroma_dir))
    
    # Additional storage directories
    storage_dirs = [
        constants.STORAGE_DIR_QDRANT,
        constants.STORAGE_DIR_WEAVIATE,
        constants.STORAGE_DIR_SOURCE_DOCS
    ]
    
    for dir_path in storage_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        logger.info(codes.DIRECTORY_CREATED, path=dir_path)


def _log_embeddings_error_help(error_str: str, logger) -> None:
    """Log helpful error messages based on error type."""
    if constants.ENV_GEMINI_API_KEY in error_str or "API key" in error_str:
        logger.error(codes.VALIDATION_ERROR, message=constants.API_KEY_ERROR_HELP)
        logger.info(codes.VALIDATION_ERROR, help=constants.GEMINI_KEY_SET_COMMAND)
        logger.info(codes.VALIDATION_ERROR, help=constants.API_KEY_GET_INSTRUCTIONS)
        return
    
    if "timeout" in error_str.lower() or "timed out" in error_str.lower():
        logger.warning(codes.VALIDATION_ERROR, message=constants.API_TIMEOUT_HELP)
        logger.info(codes.VALIDATION_ERROR, help=constants.API_TIMEOUT_NETWORK)
        logger.info(codes.VALIDATION_ERROR, help=constants.API_TIMEOUT_SERVICE)
        logger.info(codes.VALIDATION_ERROR, help=constants.API_TIMEOUT_FIREWALL)


def test_embeddings(config: Config, logger) -> bool:
    """Test embeddings provider connection."""
    logger.info(codes.TEST_STARTING, test_type="embeddings", message=constants.TESTING_EMBEDDINGS)
    logger.info(
        codes.EMBEDDINGS_INITIALIZING,
        provider=config.embeddings.provider,
        model=config.embeddings.google.model,
        message=constants.EMBEDDINGS_API_WAIT
    )
    
    try:
        embeddings = create_embeddings(config)
        logger.info(codes.EMBEDDINGS_GENERATING, text_length=len(constants.TEST_SENTENCE), message=constants.GENERATING_EMBEDDING)
        
        embedding = embeddings.embed_query(constants.TEST_SENTENCE)
        
        if not embedding or len(embedding) == 0:
            logger.error(codes.EMBEDDINGS_ERROR, message=constants.EMPTY_EMBEDDING_RETURNED)
            return False
        
        logger.info(
            codes.EMBEDDINGS_GENERATED,
            dimension=len(embedding),
            message=f"Success! Generated embedding with {len(embedding)} dimensions"
        )
        logger.info(codes.TEST_PASSED, test_type="embeddings")
        return True
        
    except KeyboardInterrupt:
        logger.warning(codes.TEST_FAILED, test_type="embeddings", reason="user_interrupted")
        raise
    except Exception as e:
        logger.error(codes.EMBEDDINGS_ERROR, error=str(e))
        _log_embeddings_error_help(str(e), logger)
        logger.error(codes.TEST_FAILED, test_type="embeddings")
        return False


def _add_test_document(vectorstore, logger) -> None:
    """Add test document to vectorstore."""
    test_metadata = {constants.TEST_DOCUMENT_SOURCE: "setup_test", "type": constants.TEST_DOCUMENT_TYPE}
    vectorstore.add_documents(
        texts=[constants.TEST_DOCUMENT_TEXT],
        metadatas=[test_metadata],
        ids=["test_doc_1"]
    )
    logger.info(codes.VECTORSTORE_DOCUMENTS_ADDED, count=1, message=constants.TEST_DOCUMENT_ADDED)


def _test_vectorstore_query(vectorstore, logger) -> bool:
    """Test vectorstore query and return success status."""
    results = vectorstore.query(constants.TEST_QUERY_TEXT, n_results=1)
    
    if not results or len(results) == 0:
        logger.error(codes.VECTORSTORE_ERROR, message=constants.NO_QUERY_RESULTS)
        return False
    
    logger.info(
        codes.VECTORSTORE_QUERY_RESULTS,
        results_count=len(results),
        message=f"Query returned {len(results)} result(s)"
    )
    return True


def test_vectorstore(config: Config, embeddings, logger) -> bool:
    """Test vectorstore initialization and basic operations."""
    logger.info(codes.TEST_STARTING, test_type="vectorstore", message=constants.TESTING_VECTORSTORE)
    logger.info(
        codes.VECTORSTORE_INITIALIZING,
        provider=config.vectorstore.provider,
        storage=config.vectorstore.chroma.persist_directory
    )
    
    try:
        vectorstore = create_vectorstore(config, embeddings)
        logger.info(codes.VECTORSTORE_INITIALIZING)
        
        vectorstore.initialize()
        logger.info(codes.VECTORSTORE_COLLECTION_CREATED, message=constants.COLLECTION_INITIALIZED)
        
        _add_test_document(vectorstore, logger)
        
        if not _test_vectorstore_query(vectorstore, logger):
            return False
        
        stats = vectorstore.get_stats()
        logger.info(codes.VECTORSTORE_STATS, stats=stats)
        
        logger.info(codes.TEST_PASSED, test_type="vectorstore")
        return True
        
    except Exception as e:
        logger.error(codes.VECTORSTORE_ERROR, error=str(e))
        logger.error(codes.TEST_FAILED, test_type="vectorstore")
        return False


def _check_python_version(logger) -> bool:
    """Check Python version meets requirements."""
    python_version = sys.version_info
    version_str = f"{python_version.major}.{python_version.minor}.{python_version.micro}"
    
    if python_version < (3, 9):
        logger.error(
            codes.PYTHON_VERSION_CHECK,
            version=version_str,
            passed=False,
            requirement=constants.PYTHON_VERSION_NEED_MIN
        )
        return False
    
    logger.info(codes.PYTHON_VERSION_CHECK, version=version_str, passed=True)
    return True


def _check_required_files(logger) -> bool:
    """Check if required files exist."""
    required_files = [
        constants.CONFIG_FILE_PATH,
        constants.CONFIG_MODULE_PATH,
        constants.EMBEDDINGS_MODULE_PATH,
        constants.VECTORSTORE_MODULE_PATH
    ]
    
    all_exist = True
    for file_path in required_files:
        if not Path(file_path).exists():
            logger.error(codes.FILE_CHECK, file=file_path, exists=False)
            all_exist = False
            continue
        
        logger.info(codes.FILE_CHECK, file=file_path, exists=True)
    
    return all_exist


def _check_environment_variables(logger) -> bool:
    """Check if required environment variables are set."""
    if not os.getenv(constants.ENV_GEMINI_API_KEY):
        logger.warning(
            codes.ENV_VAR_CHECK,
            var=constants.ENV_GEMINI_API_KEY,
            set=False,
            message="GEMINI_API_KEY not set (required for embeddings)"
        )
        logger.info(codes.ENV_VAR_CHECK, help=f"Run: export {constants.ENV_GEMINI_API_KEY}='your-key'")
        return False
    
    logger.info(codes.ENV_VAR_CHECK, var=constants.ENV_GEMINI_API_KEY, set=True)
    return True


def check_prerequisites(logger) -> bool:
    """Check if all prerequisites are met."""
    logger.info(codes.PREREQUISITES_CHECKING, message=constants.CHECK_PREREQUISITES)
    
    python_ok = _check_python_version(logger)
    files_ok = _check_required_files(logger)
    env_ok = _check_environment_variables(logger)
    
    all_good = python_ok and files_ok and env_ok
    
    if not all_good:
        logger.error(codes.PREREQUISITES_FAILED, message=constants.PREREQUISITES_NOT_MET)
        return all_good
    
    logger.info(codes.PREREQUISITES_PASSED)
    return all_good


def _log_setup_success(config: Config, logger) -> None:
    """Log successful setup completion with summary and next steps."""
    logger.info(codes.SCRIPT_COMPLETED, separator=constants.SEPARATOR_HEAVY)
    logger.info(codes.SCRIPT_COMPLETED, header=constants.SETUP_COMPLETE_HEADER)
    logger.info(codes.SCRIPT_COMPLETED, separator=constants.SEPARATOR_HEAVY)
    
    logger.info(codes.SCRIPT_COMPLETED, section=constants.SUMMARY_HEADER)
    logger.info(
        codes.SCRIPT_COMPLETED,
        vectorstore=f"{config.vectorstore.provider} (ChromaDB)",
        embeddings=f"{config.embeddings.provider} (Google)",
        storage=config.vectorstore.chroma.persist_directory,
        collection=config.vectorstore.collection_name
    )
    
    logger.info(codes.SCRIPT_COMPLETED, section=constants.NEXT_STEPS_HEADER)
    logger.info(codes.SCRIPT_COMPLETED, step=constants.NEXT_STEP_PLACE_DOCUMENTS)
    logger.info(codes.SCRIPT_COMPLETED, step=constants.NEXT_STEP_RUN_INGESTION)
    logger.info(codes.SCRIPT_COMPLETED, step=constants.NEXT_STEP_TRY_EXAMPLES)
    logger.info(codes.SCRIPT_COMPLETED, example=constants.EXAMPLE_DEMO_VECTORSTORE)
    logger.info(codes.SCRIPT_COMPLETED, example=constants.EXAMPLE_DEMO_PROVIDER_SWITCHING)
    
    logger.info(codes.SCRIPT_COMPLETED, tip=constants.SWITCH_PROVIDERS_TIP)
    logger.info(codes.SCRIPT_COMPLETED, tip=constants.SWITCH_PROVIDERS_EDIT_CONFIG)
    logger.info(codes.SCRIPT_COMPLETED, tip=constants.SWITCH_PROVIDERS_CHANGE_SETTING)
    logger.info(codes.SCRIPT_COMPLETED, tip=constants.SWITCH_PROVIDERS_SEE_DOCS)


def main():
    """Main setup function."""
    logger.info(codes.SCRIPT_STARTED, script="setup_database", header=constants.SETUP_HEADER)
    logger.info(codes.SCRIPT_STARTED, separator=constants.SEPARATOR_HEAVY)
    
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        logger.warning(codes.VALIDATION_ERROR, message=constants.VENV_WARNING)
        logger.info(codes.VALIDATION_ERROR, help=constants.VENV_RECOMMENDATION)
    
    if not check_prerequisites(logger):
        return constants.SCRIPT_EXIT_ERROR
    
    logger.info(codes.CONFIG_LOADING, message=constants.LOADING_CONFIGURATION)
    try:
        config = Config()
        logger.info(codes.CONFIG_LOADED, message=constants.CONFIGURATION_LOADED)
    except Exception as e:
        logger.error(codes.CONFIG_LOAD_FAILED, error=str(e), message=constants.FAILED_TO_LOAD_CONFIG)
        return constants.SCRIPT_EXIT_ERROR
    
    setup_logging(config.logging, config.app)
    logger.info(codes.EVENT_APP_STARTED, script="setup_database")
    
    try:
        create_storage_directories(config, logger)
    except Exception as e:
        logger.error(codes.DIRECTORY_CREATING, error=str(e), message=constants.FAILED_TO_CREATE_DIRECTORIES)
        return constants.SCRIPT_EXIT_ERROR
    
    if not test_embeddings(config, logger):
        logger.error(codes.TEST_FAILED, message=constants.EMBEDDINGS_TEST_FAILED)
        return constants.SCRIPT_EXIT_ERROR
    
    embeddings = create_embeddings(config)
    if not test_vectorstore(config, embeddings, logger):
        logger.error(codes.TEST_FAILED, message=constants.VECTORSTORE_TEST_FAILED)
        return constants.SCRIPT_EXIT_ERROR
    
    _log_setup_success(config, logger)
    logger.info(codes.EVENT_APP_SHUTDOWN, script="setup_database", status="success")
    return constants.SCRIPT_EXIT_SUCCESS


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.warning(codes.EVENT_APP_SHUTDOWN, script="setup_database", reason="interrupted")
        sys.exit(constants.SCRIPT_EXIT_ERROR)
    except Exception as e:
        logger.error(codes.OPERATION_FAILED, error=str(e), message=constants.UNEXPECTED_ERROR, exc_info=True)
        sys.exit(constants.SCRIPT_EXIT_ERROR)
