"""Developer documentation router."""

import os
from pathlib import Path
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/devdocs", tags=["devdocs"])


class DocFile(BaseModel):
    """Documentation file metadata."""

    name: str
    path: str
    type: str  # 'markdown', 'python', 'text'
    category: str  # 'docs', 'examples', 'root'


class DocContent(BaseModel):
    """Documentation content."""

    name: str
    path: str
    type: str
    content: str


def get_project_root() -> Path:
    """Get project root directory."""
    current_file = Path(__file__)
    return current_file.parent.parent.parent


def get_file_type(filename: str) -> str:
    """Determine file type from extension."""
    ext = Path(filename).suffix.lower()
    if ext == ".md":
        return "markdown"
    elif ext == ".py":
        return "python"
    else:
        return "text"


@router.get("/list", response_model=List[DocFile])
async def list_documentation_files(response: Response):
    """
    List all available documentation files.

    Returns:
        List of documentation files with metadata
    """
    # Prevent browser caching - always fetch fresh list
    response.headers["Cache-Control"] = "no-cache, must-revalidate"

    project_root = get_project_root()
    docs = []

    # Add README.md
    readme_path = project_root / "README.md"
    if readme_path.exists():
        docs.append(
            DocFile(
                name="README.md",
                path="README.md",
                type=get_file_type("README.md"),
                category="root",
            )
        )

    # Add docs/*.md files
    docs_dir = project_root / "docs"
    if docs_dir.exists():
        for doc_file in sorted(docs_dir.glob("*.md")):
            docs.append(
                DocFile(
                    name=doc_file.name,
                    path=f"docs/{doc_file.name}",
                    type=get_file_type(doc_file.name),
                    category="docs",
                )
            )

    # Add examples/*.py files
    examples_dir = project_root / "examples"
    if examples_dir.exists():
        for example_file in sorted(examples_dir.glob("*.py")):
            docs.append(
                DocFile(
                    name=example_file.name,
                    path=f"examples/{example_file.name}",
                    type=get_file_type(example_file.name),
                    category="examples",
                )
            )

    return docs


@router.get("/content", response_model=DocContent)
async def get_documentation_content(file_path: str, response: Response):
    """
    Get content of a specific documentation file.

    Args:
        file_path: Relative path to the documentation file

    Returns:
        Documentation file content

    Raises:
        HTTPException: If file not found or invalid path
    """
    # Prevent browser caching - always fetch fresh content
    response.headers["Cache-Control"] = "no-cache, must-revalidate"

    project_root = get_project_root()

    # Security: only allow specific directories
    allowed_prefixes = ["README.md", "docs/", "examples/"]
    if not any(file_path.startswith(prefix) for prefix in allowed_prefixes):
        raise HTTPException(status_code=403, detail="Access denied")

    file_full_path = project_root / file_path

    # Security: prevent directory traversal
    try:
        file_full_path = file_full_path.resolve()
        project_root_resolved = project_root.resolve()
        if not str(file_full_path).startswith(str(project_root_resolved)):
            raise HTTPException(status_code=403, detail="Access denied")
    except Exception:
        raise HTTPException(status_code=403, detail="Invalid path")

    if not file_full_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    if not file_full_path.is_file():
        raise HTTPException(status_code=400, detail="Not a file")

    try:
        content = file_full_path.read_text(encoding="utf-8")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")

    return DocContent(
        name=file_full_path.name,
        path=file_path,
        type=get_file_type(file_full_path.name),
        content=content,
    )
