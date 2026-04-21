import io
from pathlib import Path

import fitz
import pytesseract
from PIL import Image


def ocr_pdf(input_path: Path, output_path: Path, language: str = "eng") -> None:
    """Apply OCR to a PDF to make it searchable."""
    doc = fitz.open(input_path)
    ocr_doc = fitz.open()

    for page in doc:
        # 1. Render page to image
        pix = page.get_pixmap(dpi=300)
        img = Image.open(io.BytesIO(pix.tobytes()))

        # 2. Get OCR as PDF bytes for this page
        # pytesseract.image_to_pdf_or_hocr returns PDF bytes if output_type is 'pdf'
        pdf_page_bytes = pytesseract.image_to_pdf_or_hocr(
            img, extension="pdf", lang=language
        )

        # 3. Insert into the new doc
        page_pdf = fitz.open("pdf", pdf_page_bytes)
        ocr_doc.insert_pdf(page_pdf)
        page_pdf.close()

    ocr_doc.save(output_path)
    ocr_doc.close()
    doc.close()


def create_blank_pdf(output_path: Path, pages: int = 1, size: str = "a4") -> None:
    """Create a blank PDF with specified number of pages and size."""
    doc = fitz.open()
    paper = fitz.paper_size(size)
    for _ in range(pages):
        doc.new_page(width=paper[0], height=paper[1])
    doc.save(output_path)
    doc.close()


def compare_pdfs(path1: Path, path2: Path, output_path: Path) -> None:
    """Compare two PDFs by overlaying them with different colors."""
    doc1 = fitz.open(path1)
    doc2 = fitz.open(path2)
    result_doc = fitz.open()

    for i in range(min(len(doc1), len(doc2))):
        p1 = doc1[i]

        # New page in result
        res_page = result_doc.new_page(width=p1.rect.width, height=p1.rect.height)

        # Overlay both documents
        res_page.show_pdf_page(res_page.rect, doc1, i)
        res_page.show_pdf_page(res_page.rect, doc2, i, overlay=True)

    result_doc.save(output_path)
    result_doc.close()
    doc1.close()
    doc2.close()
