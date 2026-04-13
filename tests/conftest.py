from pathlib import Path

import fitz
import pytest


@pytest.fixture
def sample_pdf(tmp_path: Path) -> Path:
    """Create a 3-page sample PDF."""
    path = tmp_path / "sample.pdf"
    doc = fitz.open()
    for i in range(3):
        page = doc.new_page()
        page.insert_text((50, 50), f"Page {i+1}")
    doc.save(path)
    doc.close()
    return path

@pytest.fixture
def another_pdf(tmp_path: Path) -> Path:
    """Create another 1-page sample PDF."""
    path = tmp_path / "another.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "Another Page")
    doc.save(path)
    doc.close()
    return path
