"""Parse uploaded files (PDF, MD, TXT) into text for knowledge graph building."""

import os
import tempfile
from pathlib import Path

import charset_normalizer


def parse_pdf(file_path: str) -> str:
    """Extract text from a PDF file using PyMuPDF."""
    import fitz  # PyMuPDF
    doc = fitz.open(file_path)
    pages = []
    for page in doc:
        pages.append(page.get_text())
    doc.close()
    return "\n\n".join(pages)


def parse_text(file_path: str) -> str:
    """Read a text/markdown file with auto-detected encoding."""
    raw = Path(file_path).read_bytes()
    result = charset_normalizer.from_bytes(raw).best()
    if result is None:
        return raw.decode("utf-8", errors="replace")
    return str(result)


def parse_file(file_path: str) -> str:
    """Parse any supported file format into text."""
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        return parse_pdf(file_path)
    elif ext in (".md", ".markdown"):
        return parse_text(file_path)
    elif ext in (".txt", ".text", ".csv"):
        return parse_text(file_path)
    else:
        # Try as text
        return parse_text(file_path)


async def save_and_parse_upload(filename: str, content: bytes) -> str:
    """Save uploaded file to temp dir and parse it."""
    ext = os.path.splitext(filename)[1].lower()
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as f:
        f.write(content)
        f.flush()
        temp_path = f.name

    try:
        text = parse_file(temp_path)
    finally:
        os.unlink(temp_path)

    return text
