from pathlib import Path

import fitz


def add_page_numbers(
    input_path: Path, 
    output_path: Path, 
    text_format: str = "Page {page} of {total}",
    fontsize: int = 10,
    margin_bottom: int = 20
) -> None:
    """Add page numbers to the bottom center of each page."""
    with fitz.open(input_path) as doc:
        total = len(doc)
        for i, page in enumerate(doc):
            text = text_format.format(page=i + 1, total=total)
            # Bottom center position
            rect = page.rect
            # Create a larger textbox at the bottom to ensure text fits
            text_rect = fitz.Rect(
                0, 
                rect.height - margin_bottom - fontsize * 2, 
                rect.width, 
                rect.height - margin_bottom
            )
            page.insert_textbox(
                text_rect,
                text,
                fontsize=fontsize,
                color=(0, 0, 0),
                align=fitz.TEXT_ALIGN_CENTER
            )
        doc.save(output_path)

def compress_pdf(input_path: Path, output_path: Path) -> None:
    """Compress PDF using garbage collection and deflation."""
    with fitz.open(input_path) as doc:
        # garbage=4 is maximum garbage collection
        doc.save(
            output_path, 
            garbage=4, 
            deflate=True, 
            clean=True
        )
