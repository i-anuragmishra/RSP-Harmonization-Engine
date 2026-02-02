"""Utility helper functions for RSP Harmonization Engine."""

import json
from pathlib import Path
from datetime import datetime
from typing import Any


def ensure_dir(path: Path) -> Path:
    """Ensure a directory exists, creating it if necessary.
    
    Args:
        path: Path to the directory
        
    Returns:
        The same path, guaranteed to exist
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def load_json(path: Path) -> dict[str, Any]:
    """Load JSON data from a file.
    
    Args:
        path: Path to the JSON file
        
    Returns:
        Parsed JSON data as a dictionary
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        json.JSONDecodeError: If the file contains invalid JSON
    """
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(data: dict[str, Any], path: Path, indent: int = 2) -> None:
    """Save data to a JSON file.
    
    Args:
        data: Data to save
        path: Path to the output file
        indent: Indentation level for pretty printing
    """
    ensure_dir(path.parent)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)


def format_date(date_str: str | None = None, fmt: str = "%Y-%m-%d") -> str:
    """Format a date string or return current date.
    
    Args:
        date_str: Optional date string to format
        fmt: Output format string
        
    Returns:
        Formatted date string
    """
    if date_str:
        # Try common date formats
        for input_fmt in ["%Y-%m-%d", "%B %Y", "%Y-%m", "%d/%m/%Y", "%m/%d/%Y"]:
            try:
                dt = datetime.strptime(date_str, input_fmt)
                return dt.strftime(fmt)
            except ValueError:
                continue
        return date_str  # Return as-is if no format matches
    return datetime.now().strftime(fmt)


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to a maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length including suffix
        suffix: String to append when truncated
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def normalize_lab_name(name: str) -> str:
    """Normalize a lab name to a consistent format.
    
    Args:
        name: Lab name in any format
        
    Returns:
        Normalized lowercase name with underscores
    """
    # Common mappings
    mappings = {
        "anthropic": "anthropic",
        "openai": "openai",
        "open ai": "openai",
        "deepmind": "deepmind",
        "google deepmind": "deepmind",
        "google": "deepmind",
        "meta": "meta",
        "facebook": "meta",
        "microsoft": "microsoft",
        "amazon": "amazon",
        "aws": "amazon",
        "xai": "xai",
        "x.ai": "xai",
        "cohere": "cohere",
        "nvidia": "nvidia",
        "magic": "magic",
        "naver": "naver",
        "g42": "g42",
    }
    
    normalized = name.lower().strip().replace("-", " ").replace("_", " ")
    return mappings.get(normalized, normalized.replace(" ", "_"))
