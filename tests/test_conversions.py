from pathlib import Path

import fitz
from PIL import Image

from manipdf.core.conversions import (
    extract_images_from_pdf,
    images_to_pdf,
    pdf_to_images,
)


def test_images_to_pdf(tmp_path: Path) -> None:
    img1 = tmp_path / "1.png"
    img2 = tmp_path / "2.png"
    Image.new("RGB", (100, 100), color="red").save(img1)
    Image.new("RGB", (100, 100), color="blue").save(img2)
    
    output = tmp_path / "images.pdf"
    images_to_pdf([img1, img2], output)
    assert output.exists()
    with fitz.open(output) as doc:
        assert len(doc) == 2

def test_pdf_to_images(sample_pdf: Path, tmp_path: Path) -> None:
    output_dir = tmp_path / "images_out"
    images = pdf_to_images(sample_pdf, output_dir)
    assert len(images) == 3
    assert all(p.exists() for p in images)

def test_extract_images_from_pdf(tmp_path: Path) -> None:
    # Create PDF with an image
    pdf_path = tmp_path / "with_image.pdf"
    img_path = tmp_path / "source.png"
    Image.new("RGB", (50, 50), color="green").save(img_path)
    
    doc = fitz.open()
    page = doc.new_page()
    page.insert_image(page.rect, filename=str(img_path))
    doc.save(pdf_path)
    doc.close()
    
    output_dir = tmp_path / "extracted"
    extracted = extract_images_from_pdf(pdf_path, output_dir)
    assert len(extracted) >= 1
    assert all(p.exists() for p in extracted)
