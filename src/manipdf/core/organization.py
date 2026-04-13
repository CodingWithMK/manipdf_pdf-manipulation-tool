from pathlib import Path

import fitz  # PyMuPDF


def merge_pdfs(input_paths: list[Path], output_path: Path) -> None:
    """Merge multiple PDFs into a single one."""
    result = fitz.open()
    for path in input_paths:
        with fitz.open(path) as m_pdf:
            result.insert_pdf(m_pdf)
    result.save(output_path)
    result.close()

def split_pdf(input_path: Path, output_dir: Path) -> list[Path]:
    """Split a PDF into individual pages."""
    output_dir.mkdir(parents=True, exist_ok=True)
    generated_files = []
    with fitz.open(input_path) as doc:
        for page_num in range(len(doc)):
            new_doc = fitz.open()
            new_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)
            out_file = output_dir / f"page_{page_num + 1}.pdf"
            new_doc.save(out_file)
            new_doc.close()
            generated_files.append(out_file)
    return generated_files

def delete_pages(input_path: Path, page_indices: list[int], output_path: Path) -> None:
    """Delete specific pages from a PDF. Indices are 0-based."""
    with fitz.open(input_path) as doc:
        doc.delete_pages(page_indices)
        doc.save(output_path)

def rotate_pages(
    input_path: Path, 
    rotations: dict[int, int], 
    output_path: Path
) -> None:
    """Rotate specific pages. rotations dict: {page_index: angle_degrees}."""
    with fitz.open(input_path) as doc:
        for page_num, angle in rotations.items():
            doc[page_num].set_rotation(angle)
        doc.save(output_path)

def extract_pages(input_path: Path, page_indices: list[int], output_path: Path) -> None:
    """Extract specific pages into a new PDF."""
    with fitz.open(input_path) as doc:
        doc.select(page_indices)
        doc.save(output_path)

def sort_pages(input_path: Path, order: list[int], output_path: Path) -> None:
    """Sort pages based on a list of indices."""
    with fitz.open(input_path) as doc:
        doc.select(order)
        doc.save(output_path)

def nup_pdf(input_path: Path, rows: int, cols: int, output_path: Path) -> None:
    """Create an N-up layout (e.g., 2x2 = 4 pages per sheet)."""
    src = fitz.open(input_path)
    doc = fitz.open()
    n_up = rows * cols
    
    # Use first page size as template
    width, height = src[0].rect.width, src[0].rect.height
    cell_w = width / cols
    cell_h = height / rows
    
    for i in range(0, len(src), n_up):
        out_page = doc.new_page(width=width, height=height)
        for j in range(n_up):
            if i + j >= len(src):
                break
            row = j // cols
            col = j % cols
            target_rect = fitz.Rect(
                col * cell_w, 
                row * cell_h, 
                (col + 1) * cell_w, 
                (row + 1) * cell_h
            )
            out_page.show_pdf_page(target_rect, src, i + j)
            
    doc.save(output_path)
    doc.close()
    src.close()

def overlay_pdf(input_path: Path, overlay_path: Path, output_path: Path) -> None:
    """Overlay (watermark/stamp) one PDF onto another."""
    with fitz.open(input_path) as src:
        with fitz.open(overlay_path) as ovl:
            for page in src:
                page.show_pdf_page(page.rect, ovl, 0)
            src.save(output_path)
