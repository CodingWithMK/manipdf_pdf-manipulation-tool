import re
from pathlib import Path
import fitz

def parse_page_intervals(interval_str: str, max_pages: int, sort_and_deduplicate: bool = True) -> list[int]:
    """
    Parse a string containing comma-separated page numbers and ranges (e.g., "1-5, 8, 11-13").
    Convert 1-indexed string inputs to 0-indexed integers.
    
    Args:
        interval_str: The string containing page numbers and ranges.
        max_pages: The total number of pages in the PDF for validation.
        sort_and_deduplicate: If True (default), deduplicates and sorts the result.
                              If False, preserves the exact order and allows duplicates.
        
    Returns:
        A list of 0-indexed page integers.
        
    Raises:
        ValueError: If the syntax is invalid or pages are out of bounds.
    """
    if not interval_str.strip():
        return []

    indices = []
    # Support "1-5, 8, 11-13" and handle optional spaces
    parts = [p.strip() for p in interval_str.split(",")]
    
    for part in parts:
        if not part:
            continue
        
        # Check for range (e.g., "1-5")
        range_match = re.match(r"^(\d+)-(\d+)$", part)
        if range_match:
            start, end = map(int, range_match.groups())
            if start > end:
                raise ValueError(f"Invalid range: {part}. Start must be less than or equal to end.")
            if start < 1 or end > max_pages:
                raise ValueError(f"Range {part} out of bounds (1-{max_pages}).")
            for i in range(start, end + 1):
                indices.append(i - 1)
        elif part.isdigit():
            val = int(part)
            if val < 1 or val > max_pages:
                raise ValueError(f"Page {val} out of bounds (1-{max_pages}).")
            indices.append(val - 1)
        else:
            raise ValueError(f"Invalid page syntax: {part}")

    if sort_and_deduplicate:
        return sorted(list(set(indices)))
    return indices

def get_page_count(input_path: Path) -> int:
    """Safely get total pages from a PDF."""
    if not input_path.exists():
        raise FileNotFoundError(f"File not found: {input_path}")
    with fitz.open(input_path) as doc:
        return len(doc)

def get_pdf_thumbnails(input_path: Path, dpi: int = 72) -> list[bytes]:
    """Generate PNG thumbnails for each page of the PDF."""
    thumbnails = []
    with fitz.open(input_path) as doc:
        for page in doc:
            pix = page.get_pixmap(dpi=dpi)
            thumbnails.append(pix.tobytes("png"))
    return thumbnails
