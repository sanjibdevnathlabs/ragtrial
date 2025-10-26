# ingestion/ingest.py

import os
import sys
import google.generativeai as genai

# --- Add the project root to the Python path ---
# This is a best practice for modular code.
# It allows us to import from the 'config' package, 
# even though this script is in a subdirectory.
# Path(__file__) is this file -> .parent is 'ingestion' -> .parent is 'rag-project'
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))
# --- End of path setup ---

# Now we can import our Config class, logger, and trace codes
from config import Config
from logger import get_logger, setup_logging
from trace import codes

# Initialize logger early (before setup_logging)
logger = get_logger(__name__)

def main():
    """
    Main function to load config and set up APIs.
    """
    # 1. Load configuration first
    try:
        app_config = Config()
    except FileNotFoundError as e:
        logger.error(codes.CONFIG_LOAD_FAILED, error=str(e), message="Configuration file not found")
        logger.info(codes.CONFIG_LOAD_FAILED, help=codes.MSG_CONFIG_FILE_ENSURE)
        sys.exit(1)
    except Exception as e:
        logger.error(codes.CONFIG_LOAD_FAILED, error=str(e), message="Error loading configuration")
        sys.exit(1)
    
    # 2. Initialize logging with loaded config
    setup_logging(app_config.logging, app_config.app)
    
    logger.info(codes.INGESTION_SCRIPT_STARTED)
    logger.info(codes.CONFIGURATION_LOADED)

    # 3. Configure the Google Gemini API
    api_key = app_config.google.api_key
    
    if not api_key:
        logger.error(
            codes.GEMINI_API_KEY_MISSING,
            message=codes.MSG_GEMINI_API_KEY_MISSING
        )
        sys.exit(1)
        
    try:
        genai.configure(api_key=api_key)
        logger.info(codes.GOOGLE_API_CONFIGURED)
        
        # Optional: A quick test to list models and confirm the key is valid
        # for model in genai.list_models():
        #     pass # Just checking if the API call works
        # logger.info(codes.API_KEY_VALIDATED)

    except Exception as e:
        logger.error(
            codes.GOOGLE_API_CONFIG_FAILED,
            error=str(e),
            exc_info=True
        )
        sys.exit(1)

    logger.info(codes.SETUP_COMPLETE, message=codes.MSG_SETUP_COMPLETE)


# This standard Python line means "run the main() function
# only when this script is executed directly"
if __name__ == "__main__":
    main()
