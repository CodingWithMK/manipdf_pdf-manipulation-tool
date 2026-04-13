from pathlib import Path

import fitz


def ocr_pdf(input_path: Path, output_path: Path, language: str = "eng") -> None:
    """Apply OCR to a PDF to make it searchable."""
    # This requires Tesseract to be installed and accessible.
    # PyMuPDF uses Tesseract if it is correctly installed.
    # Note: fitz has high-level ocr_pdf through specific API
    pass

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
