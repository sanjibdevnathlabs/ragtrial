"""
Ingestion script entry point for loading and processing documents.
"""

import sys
from pathlib import Path

import google.generativeai as genai

project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

import constants
from config import Config
from logger import get_logger, setup_logging
from trace import codes

logger = get_logger(__name__)


def main():
    """Main function to load config and set up APIs."""
    try:
        app_config = Config()
    except FileNotFoundError as e:
        logger.error(codes.CONFIG_LOAD_FAILED, error=str(e), message=constants.CONFIG_FILE_NOT_FOUND)
        logger.info(codes.CONFIG_LOAD_FAILED, help=codes.MSG_CONFIG_FILE_ENSURE)
        sys.exit(1)
    except Exception as e:
        logger.error(codes.CONFIG_LOAD_FAILED, error=str(e), message=constants.ERROR_LOADING_CONFIGURATION)
        sys.exit(1)
    
    setup_logging(app_config.logging, app_config.app)
    
    logger.info(codes.INGESTION_SCRIPT_STARTED)
    logger.info(codes.CONFIGURATION_LOADED)

    api_key = app_config.google.api_key
    
    if not api_key:
        logger.error(codes.GEMINI_API_KEY_MISSING, message=codes.MSG_GEMINI_API_KEY_MISSING)
        sys.exit(1)
        
    try:
        genai.configure(api_key=api_key)
        logger.info(codes.GOOGLE_API_CONFIGURED)
    except Exception as e:
        logger.error(codes.GOOGLE_API_CONFIG_FAILED, error=str(e), exc_info=True)
        sys.exit(1)

    logger.info(codes.SETUP_COMPLETE, message=codes.MSG_SETUP_COMPLETE)


if __name__ == "__main__":
    main()
