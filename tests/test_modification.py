from pathlib import Path

import fitz

from manipdf.core.modification import add_page_numbers, compress_pdf


def test_add_page_numbers(sample_pdf: Path, tmp_path: Path) -> None:
    output = tmp_path / "numbered.pdf"
    add_page_numbers(sample_pdf, output)
    assert output.exists()
    with fitz.open(output) as doc:
        # Check first page
        assert "Page 1 of 3" in doc[0].get_text()
        # Check last page
        assert "Page 3 of 3" in doc[2].get_text()

def test_compress_pdf(sample_pdf: Path, tmp_path: Path) -> None:
    output = tmp_path / "compressed.pdf"
    compress_pdf(sample_pdf, output)
    assert output.exists()
    # For a small file, it might not be smaller, but we check if it's still a valid PDF
    with fitz.open(output) as doc:
        assert len(doc) == 3
