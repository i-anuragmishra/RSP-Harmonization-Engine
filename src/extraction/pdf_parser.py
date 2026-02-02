"""PDF parsing utilities for RSP document extraction."""

import re
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

import fitz  # PyMuPDF
import pdfplumber


@dataclass
class DocumentMetadata:
    """Metadata extracted from a PDF document."""
    filename: str
    title: Optional[str]
    author: Optional[str]
    creation_date: Optional[str]
    page_count: int
    file_size_bytes: int


def extract_text_from_pdf(pdf_path: Path) -> str:
    """Extract text content from a PDF file.
    
    Uses PyMuPDF (fitz) for primary extraction with fallback to pdfplumber
    for better table handling.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Extracted text as a single string
        
    Raises:
        FileNotFoundError: If the PDF file doesn't exist
        ValueError: If the file cannot be parsed
    """
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    try:
        # Primary extraction with PyMuPDF
        doc = fitz.open(pdf_path)
        text_parts = []
        
        for page_num, page in enumerate(doc):
            # Extract text with layout preservation
            text = page.get_text("text")
            
            # Clean up common PDF artifacts
            text = _clean_pdf_text(text)
            
            if text.strip():
                text_parts.append(f"--- Page {page_num + 1} ---\n{text}")
        
        doc.close()
        
        full_text = "\n\n".join(text_parts)
        
        # If PyMuPDF extraction seems poor, try pdfplumber
        if len(full_text) < 100 or _is_mostly_garbage(full_text):
            full_text = _extract_with_pdfplumber(pdf_path)
        
        return full_text
        
    except Exception as e:
        raise ValueError(f"Failed to parse PDF {pdf_path}: {e}")


def _extract_with_pdfplumber(pdf_path: Path) -> str:
    """Fallback extraction using pdfplumber (better for tables)."""
    text_parts = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            
            # Also extract tables
            tables = page.extract_tables()
            for table in tables:
                if table:
                    table_text = _format_table(table)
                    text += f"\n\n[TABLE]\n{table_text}\n[/TABLE]\n"
            
            if text.strip():
                text_parts.append(f"--- Page {page_num + 1} ---\n{text}")
    
    return "\n\n".join(text_parts)


def _format_table(table: list[list]) -> str:
    """Format a table as readable text."""
    if not table:
        return ""
    
    lines = []
    for row in table:
        cells = [str(cell) if cell else "" for cell in row]
        lines.append(" | ".join(cells))
    
    return "\n".join(lines)


def _clean_pdf_text(text: str) -> str:
    """Clean up common PDF text extraction artifacts."""
    # Remove excessive whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' {2,}', ' ', text)
    
    # Fix common ligature issues
    replacements = {
        'ﬁ': 'fi',
        'ﬂ': 'fl',
        'ﬀ': 'ff',
        'ﬃ': 'ffi',
        'ﬄ': 'ffl',
        '"': '"',
        '"': '"',
        ''': "'",
        ''': "'",
        '–': '-',
        '—': '-',
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    # Remove page headers/footers (common patterns)
    text = re.sub(r'^Page \d+ of \d+\s*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\d+\s*$', '', text, flags=re.MULTILINE)  # Standalone page numbers
    
    return text.strip()


def _is_mostly_garbage(text: str) -> bool:
    """Check if extracted text appears to be mostly garbage."""
    if not text:
        return True
    
    # Check ratio of alphanumeric to total characters
    alnum_count = sum(1 for c in text if c.isalnum())
    total_count = len(text)
    
    if total_count == 0:
        return True
    
    ratio = alnum_count / total_count
    return ratio < 0.3  # Less than 30% alphanumeric is suspicious


def chunk_document(text: str, max_tokens: int = 8000, overlap: int = 500) -> list[str]:
    """Split a document into chunks suitable for LLM processing.
    
    Args:
        text: Full document text
        max_tokens: Maximum tokens per chunk (approximate)
        overlap: Number of tokens to overlap between chunks
        
    Returns:
        List of text chunks
    """
    # Approximate tokens as words * 1.3
    words = text.split()
    words_per_chunk = int(max_tokens / 1.3)
    overlap_words = int(overlap / 1.3)
    
    if len(words) <= words_per_chunk:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(words):
        end = start + words_per_chunk
        
        # Try to break at paragraph boundaries
        chunk_words = words[start:end]
        chunk_text = " ".join(chunk_words)
        
        # Find a good break point (paragraph or sentence end)
        if end < len(words):
            # Look for paragraph break
            para_break = chunk_text.rfind("\n\n")
            if para_break > len(chunk_text) * 0.7:
                chunk_text = chunk_text[:para_break]
                end = start + len(chunk_text.split())
            else:
                # Look for sentence end
                sent_break = max(
                    chunk_text.rfind(". "),
                    chunk_text.rfind(".\n"),
                    chunk_text.rfind("? "),
                    chunk_text.rfind("! ")
                )
                if sent_break > len(chunk_text) * 0.7:
                    chunk_text = chunk_text[:sent_break + 1]
                    end = start + len(chunk_text.split())
        
        chunks.append(chunk_text.strip())
        start = end - overlap_words
    
    return chunks


def get_document_metadata(pdf_path: Path) -> DocumentMetadata:
    """Extract metadata from a PDF file.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        DocumentMetadata object with extracted information
    """
    pdf_path = Path(pdf_path)
    
    doc = fitz.open(pdf_path)
    metadata = doc.metadata
    
    result = DocumentMetadata(
        filename=pdf_path.name,
        title=metadata.get("title") or None,
        author=metadata.get("author") or None,
        creation_date=metadata.get("creationDate") or None,
        page_count=len(doc),
        file_size_bytes=pdf_path.stat().st_size,
    )
    
    doc.close()
    return result


def find_rsp_documents(directory: Path) -> list[Path]:
    """Find all RSP PDF documents in a directory.
    
    Args:
        directory: Directory to search
        
    Returns:
        List of paths to PDF files
    """
    directory = Path(directory)
    if not directory.exists():
        return []
    
    # Look for PDFs with RSP-related names
    pdfs = list(directory.glob("*.pdf"))
    
    # Sort by name for consistent ordering
    pdfs.sort(key=lambda p: p.stem.lower())
    
    return pdfs


def extract_sections(text: str) -> dict[str, str]:
    """Attempt to identify and extract sections from document text.
    
    Args:
        text: Full document text
        
    Returns:
        Dictionary mapping section names to content
    """
    sections = {}
    
    # Common section patterns in RSP documents
    section_patterns = [
        r'^#+\s*(.+?)$',  # Markdown headers
        r'^([A-Z][A-Z\s]{2,})$',  # ALL CAPS headers
        r'^(\d+\.?\s+[A-Z].+?)$',  # Numbered sections
        r'^((?:Section|Chapter|Part)\s+\d+[:\.]?\s*.+?)$',  # Explicit section markers
    ]
    
    current_section = "Introduction"
    current_content = []
    
    for line in text.split('\n'):
        is_header = False
        
        for pattern in section_patterns:
            match = re.match(pattern, line.strip(), re.MULTILINE)
            if match:
                # Save previous section
                if current_content:
                    sections[current_section] = '\n'.join(current_content).strip()
                
                current_section = match.group(1).strip()
                current_content = []
                is_header = True
                break
        
        if not is_header:
            current_content.append(line)
    
    # Save last section
    if current_content:
        sections[current_section] = '\n'.join(current_content).strip()
    
    return sections
