from pathlib import Path

import fitz

from manipdf.core.organization import (
    delete_pages,
    extract_pages,
    merge_pdfs,
    rotate_pages,
    sort_pages,
    split_pdf,
)


def test_merge_pdfs(sample_pdf: Path, another_pdf: Path, tmp_path: Path) -> None:
    output = tmp_path / "merged.pdf"
    merge_pdfs([sample_pdf, another_pdf], output)
    assert output.exists()
    with fitz.open(output) as doc:
        assert len(doc) == 4

def test_split_pdf(sample_pdf: Path, tmp_path: Path) -> None:
    output_dir = tmp_path / "split"
    generated = split_pdf(sample_pdf, output_dir)
    assert len(generated) == 3
    assert all(p.exists() for p in generated)

def test_delete_pages(sample_pdf: Path, tmp_path: Path) -> None:
    output = tmp_path / "deleted.pdf"
    delete_pages(sample_pdf, [0], output)  # Delete first page
    with fitz.open(output) as doc:
        assert len(doc) == 2
        assert doc[0].get_text().strip() == "Page 2"

def test_rotate_pages(sample_pdf: Path, tmp_path: Path) -> None:
    output = tmp_path / "rotated.pdf"
    rotate_pages(sample_pdf, {0: 90}, output)
    with fitz.open(output) as doc:
        assert doc[0].rotation == 90

def test_extract_pages(sample_pdf: Path, tmp_path: Path) -> None:
    output = tmp_path / "extracted.pdf"
    extract_pages(sample_pdf, [0, 2], output)
    with fitz.open(output) as doc:
        assert len(doc) == 2
        assert doc[0].get_text().strip() == "Page 1"
        assert doc[1].get_text().strip() == "Page 3"

def test_sort_pages(sample_pdf: Path, tmp_path: Path) -> None:
    output = tmp_path / "sorted.pdf"
    sort_pages(sample_pdf, [2, 1, 0], output)
    with fitz.open(output) as doc:
        assert doc[0].get_text().strip() == "Page 3"
        assert doc[2].get_text().strip() == "Page 1"

def test_nup_pdf(sample_pdf: Path, tmp_path: Path) -> None:
    output = tmp_path / "nup.pdf"
    # 2x2 n-up of a 3-page PDF should result in 1 page
    from manipdf.core.organization import nup_pdf
    nup_pdf(sample_pdf, 2, 2, output)
    assert output.exists()
    with fitz.open(output) as doc:
        assert len(doc) == 1

def test_overlay_pdf(sample_pdf: Path, tmp_path: Path) -> None:
    output = tmp_path / "overlaid.pdf"
    overlay_path = tmp_path / "overlay.pdf"
    from manipdf.core.advanced import create_blank_pdf
    create_blank_pdf(overlay_path, pages=1)
    
    from manipdf.core.organization import overlay_pdf
    overlay_pdf(sample_pdf, overlay_path, output)
    assert output.exists()
    with fitz.open(output) as doc:
        assert len(doc) == 3
