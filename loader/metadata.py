"""
Document Metadata Enrichment.

Handles enrichment of document metadata with file information.
Follows Single Responsibility Principle - metadata handling only.
"""

from pathlib import Path
from typing import List

from langchain_core.documents import Document

import constants


class DocumentMetadataEnricher:
    """Enriches documents with file metadata.

    Adds file-level information to document metadata including
    source path, file type, and file size.
    """

    @staticmethod
    def enrich(documents: List[Document], file_path: Path) -> List[Document]:
        """Enrich documents with file metadata.

        Adds source, file_type, and file_size_bytes to each document's
        metadata dictionary. Creates metadata dict if it doesn't exist.

        Args:
            documents: List of documents to enrich
            file_path: Path to source file

        Returns:
            List of documents with enriched metadata (same objects, modified in place)
        """
        file_size = file_path.stat().st_size
        file_type = FileTypeMapper.get_type(file_path)

        for doc in documents:
            if doc.metadata is None:
                doc.metadata = {}

            doc.metadata[constants.META_SOURCE] = str(file_path)
            doc.metadata[constants.META_FILE_TYPE] = file_type
            doc.metadata[constants.META_FILE_SIZE] = file_size

        return documents


class FileTypeMapper:
    """Maps file extensions to human-readable file types.

    Provides consistent type identifiers for different file formats.
    """

    _TYPE_MAP = {
        constants.EXT_PDF: constants.FILE_TYPE_PDF,
        constants.EXT_TXT: constants.FILE_TYPE_TXT,
        constants.EXT_MD: constants.FILE_TYPE_MD,
        constants.EXT_DOCX: constants.FILE_TYPE_DOCX,
        constants.EXT_CSV: constants.FILE_TYPE_CSV,
        constants.EXT_JSON: constants.FILE_TYPE_JSON,
    }

    @classmethod
    def get_type(cls, file_path: Path) -> str:
        """Get human-readable file type from extension.

        Args:
            file_path: Path to file

        Returns:
            File type identifier (e.g., 'pdf', 'text', 'markdown')
        """
        extension = file_path.suffix.lower()
        return cls._TYPE_MAP.get(extension, constants.FILE_TYPE_UNKNOWN)
