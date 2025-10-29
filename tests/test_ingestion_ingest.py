"""
Tests for ingestion pipeline.

Tests document ingestion business logic with database-driven processing.
"""

import argparse
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from ingestion.ingest import (
    ingest_documents,
    main,
    parse_arguments,
    print_summary,
    process_file,
    scan_directory,
)

# ============================================================================
# Test parse_arguments
# ============================================================================


class TestParseArguments:
    """Test suite for argument parsing."""

    def test_parse_arguments_default(self):
        """Test default arguments (no flags)."""
        with patch("sys.argv", ["ingest.py"]):
            args = parse_arguments()

            assert args.clear is False

    def test_parse_arguments_with_clear_flag(self):
        """Test with --clear flag."""
        with patch("sys.argv", ["ingest.py", "--clear"]):
            args = parse_arguments()

            assert args.clear is True


# ============================================================================
# Test scan_directory
# ============================================================================


class TestScanDirectory:
    """Test suite for directory scanning."""

    def test_scan_directory_success(self, tmp_path):
        """Test scanning directory with supported files."""
        # Create test files
        (tmp_path / "file1.txt").touch()
        (tmp_path / "file2.pdf").touch()
        (tmp_path / "file3.md").touch()
        (tmp_path / "ignored.exe").touch()

        with patch("loader.factory.LoaderFactory.get_supported_extensions") as mock_ext:
            mock_ext.return_value = [".txt", ".pdf", ".md"]

            files = scan_directory(tmp_path)

            assert len(files) == 3
            assert all(isinstance(f, Path) for f in files)
            # Files should be sorted
            assert files[0].name == "file1.txt"
            assert files[1].name == "file2.pdf"
            assert files[2].name == "file3.md"

    def test_scan_directory_not_found(self):
        """Test error when directory doesn't exist."""
        non_existent = Path("/non/existent/path")

        with pytest.raises(FileNotFoundError) as exc_info:
            scan_directory(non_existent)

        assert "not found" in str(exc_info.value).lower()

    def test_scan_directory_not_a_directory(self, tmp_path):
        """Test error when path is a file, not directory."""
        file_path = tmp_path / "file.txt"
        file_path.touch()

        with pytest.raises(NotADirectoryError):
            scan_directory(file_path)

    def test_scan_directory_empty(self, tmp_path):
        """Test scanning empty directory."""
        with patch("loader.factory.LoaderFactory.get_supported_extensions") as mock_ext:
            mock_ext.return_value = [".txt", ".pdf"]

            files = scan_directory(tmp_path)

            assert files == []

    def test_scan_directory_filters_by_extension(self, tmp_path):
        """Test that only supported extensions are included."""
        (tmp_path / "doc.txt").touch()
        (tmp_path / "image.jpg").touch()
        (tmp_path / "video.mp4").touch()

        with patch("loader.factory.LoaderFactory.get_supported_extensions") as mock_ext:
            mock_ext.return_value = [".txt"]

            files = scan_directory(tmp_path)

            assert len(files) == 1
            assert files[0].name == "doc.txt"


# ============================================================================
# Test process_file
# ============================================================================


class TestProcessFile:
    """Test suite for file processing."""

    def test_process_file_success(self):
        """Test successful file processing."""
        file_path = Path("test.pdf")
        mock_loader = Mock()
        mock_splitter = Mock()

        # Mock document loading
        mock_doc = Mock()
        mock_loader.load_document.return_value = [mock_doc]

        # Mock splitting
        mock_chunk = Mock()
        mock_splitter.split_documents.return_value = [mock_chunk, mock_chunk]

        success, chunk_count, error_msg = process_file(
            file_path, mock_loader, mock_splitter
        )

        assert success is True
        assert chunk_count == 2
        assert error_msg == ""

        mock_loader.load_document.assert_called_once_with(file_path)
        mock_splitter.split_documents.assert_called_once_with([mock_doc])

    def test_process_file_no_documents_loaded(self):
        """Test when no documents are loaded."""
        file_path = Path("test.pdf")
        mock_loader = Mock()
        mock_splitter = Mock()

        mock_loader.load_document.return_value = []

        success, chunk_count, error_msg = process_file(
            file_path, mock_loader, mock_splitter
        )

        assert success is False
        assert chunk_count == 0
        assert "No documents loaded" in error_msg

    def test_process_file_no_chunks_created(self):
        """Test when no chunks are created."""
        file_path = Path("test.pdf")
        mock_loader = Mock()
        mock_splitter = Mock()

        mock_doc = Mock()
        mock_loader.load_document.return_value = [mock_doc]
        mock_splitter.split_documents.return_value = []

        success, chunk_count, error_msg = process_file(
            file_path, mock_loader, mock_splitter
        )

        assert success is False
        assert chunk_count == 0
        assert "No chunks created" in error_msg

    def test_process_file_loader_exception(self):
        """Test exception during document loading."""
        file_path = Path("test.pdf")
        mock_loader = Mock()
        mock_splitter = Mock()

        mock_loader.load_document.side_effect = Exception("Load error")

        success, chunk_count, error_msg = process_file(
            file_path, mock_loader, mock_splitter
        )

        assert success is False
        assert chunk_count == 0
        assert "Load error" in error_msg

    def test_process_file_splitter_exception(self):
        """Test exception during document splitting."""
        file_path = Path("test.pdf")
        mock_loader = Mock()
        mock_splitter = Mock()

        mock_doc = Mock()
        mock_loader.load_document.return_value = [mock_doc]
        mock_splitter.split_documents.side_effect = Exception("Split error")

        success, chunk_count, error_msg = process_file(
            file_path, mock_loader, mock_splitter
        )

        assert success is False
        assert chunk_count == 0
        assert "Split error" in error_msg


# ============================================================================
# Test ingest_documents
# ============================================================================


class TestIngestDocuments:
    """Test suite for document ingestion."""

    @pytest.fixture
    def mock_config(self):
        """Mock configuration."""
        config = Mock()
        config.vectorstore = Mock()
        config.embeddings = Mock()
        return config

    @pytest.fixture
    def mock_file_service(self):
        """Mock file service."""
        return Mock()

    @pytest.fixture
    def mock_vectorstore(self):
        """Mock vectorstore."""
        vectorstore = Mock()
        vectorstore.initialize = Mock()
        vectorstore.clear = Mock()
        vectorstore.add_documents = Mock()
        return vectorstore

    @pytest.fixture
    def mock_embeddings(self):
        """Mock embeddings."""
        return Mock()

    @pytest.fixture
    def mock_loader(self):
        """Mock document loader."""
        loader = Mock()
        return loader

    @pytest.fixture
    def mock_splitter(self):
        """Mock document splitter."""
        splitter = Mock()
        return splitter

    def test_ingest_no_unindexed_files(self, mock_config, mock_file_service):
        """Test ingestion with no unindexed files."""
        with patch("ingestion.ingest.FileService", return_value=mock_file_service):
            mock_file_service.get_unindexed_files.return_value = []

            successful, failed, skipped, total_chunks = ingest_documents(mock_config)

            assert successful == 0
            assert failed == 0
            assert skipped == 0
            assert total_chunks == 0

    def test_ingest_single_file_success(
        self,
        mock_config,
        mock_file_service,
        mock_vectorstore,
        mock_embeddings,
        mock_loader,
        mock_splitter,
        tmp_path,
    ):
        """Test successful ingestion of single file."""
        # Create test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")

        # Mock file service
        mock_file_service.get_unindexed_files.return_value = [
            {"id": "file-123", "filename": "test.txt", "file_path": str(test_file)}
        ]

        # Mock document and chunks
        mock_doc = Mock()
        mock_doc.page_content = "test content"
        mock_doc.metadata = {}

        mock_chunk = Mock()
        mock_chunk.page_content = "test content"
        mock_chunk.metadata = {}

        mock_loader.load_document.return_value = [mock_doc]
        mock_splitter.split_documents.return_value = [mock_chunk]

        with patch(
            "ingestion.ingest.FileService", return_value=mock_file_service
        ), patch(
            "ingestion.ingest.create_embeddings", return_value=mock_embeddings
        ), patch(
            "ingestion.ingest.create_vectorstore", return_value=mock_vectorstore
        ), patch(
            "ingestion.ingest.DocumentLoader", return_value=mock_loader
        ), patch(
            "ingestion.ingest.DocumentSplitter", return_value=mock_splitter
        ), patch(
            "ingestion.ingest.LoaderFactory.is_supported", return_value=True
        ):

            successful, failed, skipped, total_chunks = ingest_documents(mock_config)

            assert successful == 1
            assert failed == 0
            assert skipped == 0
            assert total_chunks == 1

            # Verify vectorstore operations
            mock_vectorstore.initialize.assert_called_once()
            mock_vectorstore.add_documents.assert_called_once()

            # Verify file marked as indexed
            mock_file_service.mark_as_indexed.assert_called_once_with("file-123")

    def test_ingest_with_clear_first(
        self,
        mock_config,
        mock_file_service,
        mock_vectorstore,
        mock_embeddings,
        mock_loader,
        mock_splitter,
        tmp_path,
    ):
        """Test ingestion with clear_first=True."""
        # Need at least one file to trigger clear (otherwise early return)
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")

        mock_file_service.get_unindexed_files.return_value = [
            {"id": "file-123", "filename": "test.txt", "file_path": str(test_file)}
        ]

        mock_doc = Mock()
        mock_doc.page_content = "content"
        mock_doc.metadata = {}

        mock_chunk = Mock()
        mock_chunk.page_content = "content"
        mock_chunk.metadata = {}

        mock_loader.load_document.return_value = [mock_doc]
        mock_splitter.split_documents.return_value = [mock_chunk]

        with patch(
            "ingestion.ingest.FileService", return_value=mock_file_service
        ), patch(
            "ingestion.ingest.create_embeddings", return_value=mock_embeddings
        ), patch(
            "ingestion.ingest.create_vectorstore", return_value=mock_vectorstore
        ), patch(
            "ingestion.ingest.DocumentLoader", return_value=mock_loader
        ), patch(
            "ingestion.ingest.DocumentSplitter", return_value=mock_splitter
        ), patch(
            "ingestion.ingest.LoaderFactory.is_supported", return_value=True
        ):

            ingest_documents(mock_config, clear_first=True)

            mock_vectorstore.clear.assert_called_once()

    def test_ingest_file_not_found_skipped(
        self, mock_config, mock_file_service, mock_vectorstore, mock_embeddings
    ):
        """Test file not found is skipped."""
        mock_file_service.get_unindexed_files.return_value = [
            {
                "id": "file-123",
                "filename": "missing.txt",
                "file_path": "/non/existent/path.txt",
            }
        ]

        with patch(
            "ingestion.ingest.FileService", return_value=mock_file_service
        ), patch(
            "ingestion.ingest.create_embeddings", return_value=mock_embeddings
        ), patch(
            "ingestion.ingest.create_vectorstore", return_value=mock_vectorstore
        ):

            successful, failed, skipped, total_chunks = ingest_documents(mock_config)

            assert successful == 0
            assert failed == 0
            assert skipped == 1
            assert total_chunks == 0

    def test_ingest_unsupported_format_skipped(
        self,
        mock_config,
        mock_file_service,
        mock_vectorstore,
        mock_embeddings,
        tmp_path,
    ):
        """Test unsupported format is skipped."""
        test_file = tmp_path / "test.exe"
        test_file.touch()

        mock_file_service.get_unindexed_files.return_value = [
            {"id": "file-123", "filename": "test.exe", "file_path": str(test_file)}
        ]

        with patch(
            "ingestion.ingest.FileService", return_value=mock_file_service
        ), patch(
            "ingestion.ingest.create_embeddings", return_value=mock_embeddings
        ), patch(
            "ingestion.ingest.create_vectorstore", return_value=mock_vectorstore
        ), patch(
            "ingestion.ingest.LoaderFactory.is_supported", return_value=False
        ):

            successful, failed, skipped, total_chunks = ingest_documents(mock_config)

            assert successful == 0
            assert failed == 0
            assert skipped == 1
            assert total_chunks == 0

    def test_ingest_file_processing_failure(
        self,
        mock_config,
        mock_file_service,
        mock_vectorstore,
        mock_embeddings,
        mock_loader,
        mock_splitter,
        tmp_path,
    ):
        """Test file processing failure."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")

        mock_file_service.get_unindexed_files.return_value = [
            {"id": "file-123", "filename": "test.txt", "file_path": str(test_file)}
        ]

        # Make loader return empty documents (failure)
        mock_loader.load_document.return_value = []

        with patch(
            "ingestion.ingest.FileService", return_value=mock_file_service
        ), patch(
            "ingestion.ingest.create_embeddings", return_value=mock_embeddings
        ), patch(
            "ingestion.ingest.create_vectorstore", return_value=mock_vectorstore
        ), patch(
            "ingestion.ingest.DocumentLoader", return_value=mock_loader
        ), patch(
            "ingestion.ingest.DocumentSplitter", return_value=mock_splitter
        ), patch(
            "ingestion.ingest.LoaderFactory.is_supported", return_value=True
        ):

            successful, failed, skipped, total_chunks = ingest_documents(mock_config)

            assert successful == 0
            assert failed == 1
            assert skipped == 0
            assert total_chunks == 0

    def test_ingest_multiple_files(
        self,
        mock_config,
        mock_file_service,
        mock_vectorstore,
        mock_embeddings,
        mock_loader,
        mock_splitter,
        tmp_path,
    ):
        """Test ingestion of multiple files."""
        # Create test files
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        file1.write_text("content 1")
        file2.write_text("content 2")

        mock_file_service.get_unindexed_files.return_value = [
            {"id": "file-1", "filename": "file1.txt", "file_path": str(file1)},
            {"id": "file-2", "filename": "file2.txt", "file_path": str(file2)},
        ]

        # Mock documents and chunks
        mock_doc = Mock()
        mock_doc.page_content = "content"
        mock_doc.metadata = {}

        mock_chunk = Mock()
        mock_chunk.page_content = "content"
        mock_chunk.metadata = {}

        mock_loader.load_document.return_value = [mock_doc]
        mock_splitter.split_documents.return_value = [mock_chunk]

        with patch(
            "ingestion.ingest.FileService", return_value=mock_file_service
        ), patch(
            "ingestion.ingest.create_embeddings", return_value=mock_embeddings
        ), patch(
            "ingestion.ingest.create_vectorstore", return_value=mock_vectorstore
        ), patch(
            "ingestion.ingest.DocumentLoader", return_value=mock_loader
        ), patch(
            "ingestion.ingest.DocumentSplitter", return_value=mock_splitter
        ), patch(
            "ingestion.ingest.LoaderFactory.is_supported", return_value=True
        ):

            successful, failed, skipped, total_chunks = ingest_documents(mock_config)

            assert successful == 2
            assert failed == 0
            assert skipped == 0
            assert total_chunks == 2

            # Verify both files marked as indexed
            assert mock_file_service.mark_as_indexed.call_count == 2

    def test_ingest_mark_as_indexed_failure(
        self,
        mock_config,
        mock_file_service,
        mock_vectorstore,
        mock_embeddings,
        mock_loader,
        mock_splitter,
        tmp_path,
    ):
        """Test that mark_as_indexed failure is logged but doesn't stop ingestion."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")

        mock_file_service.get_unindexed_files.return_value = [
            {"id": "file-123", "filename": "test.txt", "file_path": str(test_file)}
        ]

        # Mock mark_as_indexed to fail
        mock_file_service.mark_as_indexed.side_effect = Exception("DB error")

        mock_doc = Mock()
        mock_doc.page_content = "content"
        mock_doc.metadata = {}

        mock_chunk = Mock()
        mock_chunk.page_content = "content"
        mock_chunk.metadata = {}

        mock_loader.load_document.return_value = [mock_doc]
        mock_splitter.split_documents.return_value = [mock_chunk]

        with patch(
            "ingestion.ingest.FileService", return_value=mock_file_service
        ), patch(
            "ingestion.ingest.create_embeddings", return_value=mock_embeddings
        ), patch(
            "ingestion.ingest.create_vectorstore", return_value=mock_vectorstore
        ), patch(
            "ingestion.ingest.DocumentLoader", return_value=mock_loader
        ), patch(
            "ingestion.ingest.DocumentSplitter", return_value=mock_splitter
        ), patch(
            "ingestion.ingest.LoaderFactory.is_supported", return_value=True
        ):

            # Should not raise exception
            successful, failed, skipped, total_chunks = ingest_documents(mock_config)

            assert successful == 1
            assert total_chunks == 1


# ============================================================================
# Test print_summary
# ============================================================================


class TestPrintSummary:
    """Test suite for summary printing."""

    def test_print_summary(self):
        """Test summary logging."""
        # Should not raise exception
        print_summary(
            successful=10, failed=2, skipped=3, total_chunks=500, duration=15.75
        )


# ============================================================================
# Test main
# ============================================================================


class TestMain:
    """Test suite for main entry point."""

    def test_main_success(self):
        """Test successful main execution."""
        mock_config = Mock()

        with patch("ingestion.ingest.parse_arguments") as mock_parse, patch(
            "ingestion.ingest.Config", return_value=mock_config
        ), patch("ingestion.ingest.setup_logging"), patch(
            "ingestion.ingest.ingest_documents", return_value=(10, 0, 0, 100)
        ), patch(
            "ingestion.ingest.print_summary"
        ):

            mock_parse.return_value = argparse.Namespace(clear=False)

            with pytest.raises(SystemExit) as exc_info:
                main()

            assert exc_info.value.code == 0

    def test_main_config_file_not_found(self):
        """Test main with config file not found."""
        with patch("ingestion.ingest.parse_arguments"), patch(
            "ingestion.ingest.Config", side_effect=FileNotFoundError("Config not found")
        ):

            with pytest.raises(SystemExit) as exc_info:
                main()

            assert exc_info.value.code == 1

    def test_main_config_load_error(self):
        """Test main with config load error."""
        with patch("ingestion.ingest.parse_arguments"), patch(
            "ingestion.ingest.Config", side_effect=Exception("Config error")
        ):

            with pytest.raises(SystemExit) as exc_info:
                main()

            assert exc_info.value.code == 1

    def test_main_with_failures(self):
        """Test main with failed files."""
        mock_config = Mock()

        with patch("ingestion.ingest.parse_arguments") as mock_parse, patch(
            "ingestion.ingest.Config", return_value=mock_config
        ), patch("ingestion.ingest.setup_logging"), patch(
            "ingestion.ingest.ingest_documents", return_value=(5, 3, 0, 50)
        ), patch(
            "ingestion.ingest.print_summary"
        ):

            mock_parse.return_value = argparse.Namespace(clear=False)

            with pytest.raises(SystemExit) as exc_info:
                main()

            assert exc_info.value.code == 1

    def test_main_no_successful_files(self):
        """Test main with no successful files."""
        mock_config = Mock()

        with patch("ingestion.ingest.parse_arguments") as mock_parse, patch(
            "ingestion.ingest.Config", return_value=mock_config
        ), patch("ingestion.ingest.setup_logging"), patch(
            "ingestion.ingest.ingest_documents", return_value=(0, 0, 5, 0)
        ), patch(
            "ingestion.ingest.print_summary"
        ):

            mock_parse.return_value = argparse.Namespace(clear=False)

            with pytest.raises(SystemExit) as exc_info:
                main()

            assert exc_info.value.code == 1

    def test_main_keyboard_interrupt(self):
        """Test main with keyboard interrupt."""
        with patch("ingestion.ingest.parse_arguments"), patch(
            "ingestion.ingest.Config", side_effect=KeyboardInterrupt()
        ):

            with pytest.raises(SystemExit) as exc_info:
                main()

            assert exc_info.value.code == 130

    def test_main_unexpected_exception(self):
        """Test main with unexpected exception."""
        with patch("ingestion.ingest.parse_arguments"), patch(
            "ingestion.ingest.Config", side_effect=RuntimeError("Unexpected error")
        ):

            with pytest.raises(SystemExit) as exc_info:
                main()

            assert exc_info.value.code == 1
