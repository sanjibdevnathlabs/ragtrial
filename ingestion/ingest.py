"""
Document Ingestion Pipeline.

Loads documents from source_docs/, processes them through the pipeline:
  1. Load documents (auto-detect format)
  2. Split into chunks
  3. Generate embeddings
  4. Store in vectorstore

Usage:
    python -m ingestion.ingest                    # Process all files
    python -m ingestion.ingest --clear            # Clear vectorstore first
    python -m ingestion.ingest --dir custom/      # Custom source directory
"""

import argparse
import sys
import time
from pathlib import Path
from typing import List, Tuple

import constants
from config import Config
from embeddings.factory import create_embeddings
from loader import DocumentLoader
from loader.factory import LoaderFactory
from logger import get_logger, setup_logging
from splitter import DocumentSplitter
from trace import codes
from vectorstore.factory import create_vectorstore


logger = get_logger(__name__)


def parse_arguments() -> argparse.Namespace:
    """
    Parse command line arguments.
    
    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description=constants.INGESTION_HEADER,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--dir",
        type=str,
        default=constants.DEFAULT_SOURCE_DIR,
        help=f"Source directory (default: {constants.DEFAULT_SOURCE_DIR})"
    )
    
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear vectorstore before ingestion"
    )
    
    return parser.parse_args()


def scan_directory(source_dir: Path) -> List[Path]:
    """
    Scan directory for supported document files.
    
    Args:
        source_dir: Directory to scan
        
    Returns:
        List of file paths
        
    Raises:
        FileNotFoundError: If directory doesn't exist
    """
    if not source_dir.exists():
        raise FileNotFoundError(f"{constants.ERROR_DIRECTORY_NOT_FOUND}: {source_dir}")
    
    if not source_dir.is_dir():
        raise NotADirectoryError(f"Not a directory: {source_dir}")
    
    logger.info(codes.INGESTION_SCANNING_DIRECTORY, directory=str(source_dir))
    
    # Get supported extensions from loader factory
    supported_extensions = LoaderFactory.get_supported_extensions()
    
    # Find all files with supported extensions
    files = []
    for ext in supported_extensions:
        pattern = f"*{ext}"
        files.extend(source_dir.glob(pattern))
    
    # Sort for consistent processing order
    files = sorted(files)
    
    return files


def process_file(
    file_path: Path,
    loader: DocumentLoader,
    splitter: DocumentSplitter
) -> Tuple[bool, int, str]:
    """
    Process single file through the pipeline.
    
    Args:
        file_path: Path to document file
        loader: Document loader instance
        splitter: Document splitter instance
        
    Returns:
        Tuple of (success, chunk_count, error_message)
    """
    try:
        # Load document
        documents = loader.load_document(file_path)
        
        if not documents:
            return False, 0, "No documents loaded"
        
        logger.info(
            codes.INGESTION_FILE_LOADED,
            filename=file_path.name,
            doc_count=len(documents)
        )
        
        # Split into chunks
        chunks = splitter.split_documents(documents)
        
        if not chunks:
            return False, 0, "No chunks created"
        
        logger.info(
            codes.INGESTION_FILE_SPLIT,
            filename=file_path.name,
            chunk_count=len(chunks)
        )
        
        return True, len(chunks), ""
        
    except Exception as e:
        error_msg = str(e)
        logger.error(
            codes.INGESTION_FILE_ERROR,
            filename=file_path.name,
            error=error_msg,
            exc_info=True
        )
        return False, 0, error_msg


def ingest_documents(
    source_dir: Path,
    config: Config,
    clear_first: bool = False
) -> Tuple[int, int, int, int]:
    """
    Ingest all documents from directory into vectorstore.
    
    Args:
        source_dir: Source directory containing documents
        config: Application configuration
        clear_first: Whether to clear vectorstore first
        
    Returns:
        Tuple of (successful, failed, skipped, total_chunks)
    """
    # Scan for files
    files = scan_directory(source_dir)
    
    if not files:
        logger.warning(codes.INGESTION_FILES_FOUND, count=0)
        logger.warning(codes.INGESTION_FILE_SKIPPED, message=codes.MSG_NO_FILES_FOUND)
        return 0, 0, 0, 0
    
    logger.info(codes.INGESTION_FILES_FOUND, count=len(files))
    
    # Initialize components
    embeddings = create_embeddings(config)
    vectorstore = create_vectorstore(config, embeddings)
    vectorstore.initialize()
    
    # Clear if requested
    if clear_first:
        logger.info(codes.INGESTION_CLEARING_VECTORSTORE)
        vectorstore.clear()
        logger.info(codes.INGESTION_VECTORSTORE_CLEARED)
    
    loader = DocumentLoader()
    splitter = DocumentSplitter()
    
    # Process files
    successful = 0
    failed = 0
    skipped = 0
    total_chunks = 0
    all_chunks = []
    
    for idx, file_path in enumerate(files, 1):
        logger.info(
            codes.INGESTION_PROCESSING_FILE,
            current=idx,
            total=len(files),
            filename=file_path.name
        )
        
        # Check if supported
        if not LoaderFactory.is_supported(file_path):
            logger.warning(
                codes.INGESTION_FILE_SKIPPED,
                filename=file_path.name,
                reason="Unsupported format"
            )
            skipped += 1
            continue
        
        # Process file
        success, chunk_count, error_msg = process_file(file_path, loader, splitter)
        
        if success:
            successful += 1
            total_chunks += chunk_count
            
            # Load and collect chunks for batch storage
            documents = loader.load_document(file_path)
            chunks = splitter.split_documents(documents)
            all_chunks.extend(chunks)
            
            logger.info(
                codes.INGESTION_FILE_SUCCESS,
                filename=file_path.name,
                chunks=chunk_count
            )
        else:
            failed += 1
            logger.error(
                codes.INGESTION_FILE_ERROR,
                filename=file_path.name,
                error=error_msg
            )
    
    # Store all chunks in vectorstore (batch operation)
    if all_chunks:
        logger.info(
            codes.INGESTION_FILE_EMBEDDED,
            chunk_count=len(all_chunks)
        )
        
        texts = [chunk.page_content for chunk in all_chunks]
        metadatas = [chunk.metadata for chunk in all_chunks]
        
        vectorstore.add_documents(texts, metadatas)
        
        logger.info(
            codes.INGESTION_FILE_STORED,
            chunk_count=len(all_chunks)
        )
    
    return successful, failed, skipped, total_chunks


def print_summary(
    successful: int,
    failed: int,
    skipped: int,
    total_chunks: int,
    duration: float
):
    """
    Print ingestion summary.
    
    Args:
        successful: Number of successful files
        failed: Number of failed files
        skipped: Number of skipped files
        total_chunks: Total chunks created
        duration: Duration in seconds
    """
    total = successful + failed + skipped
    
    logger.info(
        codes.INGESTION_COMPLETE,
        total_files=total,
        successful=successful,
        failed=failed,
        skipped=skipped,
        total_chunks=total_chunks,
        duration_seconds=f"{duration:.2f}"
    )


def main():
    """Main ingestion pipeline entry point."""
    try:
        # Parse arguments
        args = parse_arguments()
        
        # Load configuration
        try:
            config = Config()
        except FileNotFoundError as e:
            logger.error(
                codes.CONFIG_LOAD_FAILED,
                error=str(e),
                message=constants.CONFIG_FILE_NOT_FOUND
            )
            logger.info(codes.CONFIG_LOAD_FAILED, help=codes.MSG_CONFIG_FILE_ENSURE)
            sys.exit(1)
        except Exception as e:
            logger.error(
                codes.CONFIG_LOAD_FAILED,
                error=str(e),
                message=constants.ERROR_LOADING_CONFIGURATION
            )
            sys.exit(1)
        
        # Setup logging
        setup_logging(config.logging, config.app)
        
        logger.info(codes.INGESTION_SCRIPT_STARTED)
        logger.info(codes.CONFIGURATION_LOADED)
        
        # Get source directory
        source_dir = Path(args.dir)
        
        # Start timer
        start_time = time.time()
        
        # Run ingestion
        successful, failed, skipped, total_chunks = ingest_documents(
            source_dir=source_dir,
            config=config,
            clear_first=args.clear
        )
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Print summary
        print_summary(successful, failed, skipped, total_chunks, duration)
        
        # Exit with appropriate code
        if failed > 0:
            sys.exit(1)
        
        if successful == 0:
            sys.exit(1)
        
        sys.exit(0)
        
    except KeyboardInterrupt:
        logger.warning("Ingestion interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error("Ingestion failed", error=str(e), exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
