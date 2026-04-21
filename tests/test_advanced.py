import pytest
from pathlib import Path
import fitz
from manipdf.core.advanced import create_blank_pdf, compare_pdfs, ocr_pdf

def test_create_blank_pdf(tmp_path: Path):
    output = tmp_path / "blank.pdf"
    create_blank_pdf(output, pages=3, size="a4")
    assert output.exists()
    with fitz.open(output) as doc:
        assert len(doc) == 3
        # A4 size is approx 595x842 points
        assert round(doc[0].rect.width) == 595
        assert round(doc[0].rect.height) == 842

def test_compare_pdfs(sample_pdf: Path, tmp_path: Path):
    output = tmp_path / "comparison.pdf"
    # Create a slightly different PDF for comparison
    another = tmp_path / "another.pdf"
    create_blank_pdf(another, pages=3)
    
    compare_pdfs(sample_pdf, another, output)
    assert output.exists()
    with fitz.open(output) as doc:
        assert len(doc) == 3

@pytest.mark.skip(reason="Tesseract might not be installed in CI environment")
def test_ocr_pdf(sample_pdf: Path, tmp_path: Path):
    output = tmp_path / "ocr_result.pdf"
    ocr_pdf(sample_pdf, output)
    assert output.exists()
