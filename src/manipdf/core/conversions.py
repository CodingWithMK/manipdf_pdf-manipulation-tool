import subprocess
from pathlib import Path

import fitz


def images_to_pdf(image_paths: list[Path], output_path: Path) -> None:
    """Convert multiple images into a single PDF."""
    doc = fitz.open()
    for img_path in image_paths:
        img_doc = fitz.open(img_path)
        pdf_bytes = img_doc.convert_to_pdf()
        img_pdf = fitz.open("pdf", pdf_bytes)
        doc.insert_pdf(img_pdf)
        img_pdf.close()
    doc.save(output_path)
    doc.close()

def pdf_to_images(input_path: Path, output_dir: Path, dpi: int = 300) -> list[Path]:
    """Render each page of a PDF as an image."""
    output_dir.mkdir(parents=True, exist_ok=True)
    image_files = []
    with fitz.open(input_path) as doc:
        for page_num in range(len(doc)):
            page = doc[page_num]
            pix = page.get_pixmap(dpi=dpi)
            out_file = output_dir / f"page_{page_num + 1}.png"
            pix.save(str(out_file))
            image_files.append(out_file)
    return image_files

def extract_images_from_pdf(input_path: Path, output_dir: Path) -> list[Path]:
    """Extract all embedded images from a PDF."""
    output_dir.mkdir(parents=True, exist_ok=True)
    extracted_images = []
    with fitz.open(input_path) as doc:
        for i, page in enumerate(doc):
            image_list = page.get_images()
            for img_index, img in enumerate(image_list):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                out_file = output_dir / f"image_p{i+1}_{img_index+1}.{image_ext}"
                with open(out_file, "wb") as f:
                    f.write(image_bytes)
                extracted_images.append(out_file)
    return extracted_images

def office_to_pdf(input_path: Path, output_dir: Path) -> Path:
    """Convert Office document to PDF using LibreOffice."""
    cmd = [
        "libreoffice", "--headless", "--convert-to", "pdf", 
        "--outdir", str(output_dir), str(input_path)
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        pdf_name = input_path.stem + ".pdf"
        return output_dir / pdf_name
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Office conversion failed: {e.stderr.decode()}") from e
    except FileNotFoundError as e:
        raise RuntimeError("LibreOffice not found. Please install it.") from e
