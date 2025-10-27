"""
Document Loader Strategies.

Individual loader implementations for different file formats.
Each strategy is a self-contained module following Single Responsibility Principle.
"""

from loader.strategies.csv import CSVLoaderStrategy
from loader.strategies.docx import DocxLoaderStrategy
from loader.strategies.json import JSONLoaderStrategy
from loader.strategies.markdown import MarkdownLoaderStrategy
from loader.strategies.pdf import PDFLoaderStrategy
from loader.strategies.text import TextLoaderStrategy

__all__ = [
    "CSVLoaderStrategy",
    "DocxLoaderStrategy",
    "JSONLoaderStrategy",
    "MarkdownLoaderStrategy",
    "PDFLoaderStrategy",
    "TextLoaderStrategy",
]

