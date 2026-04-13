from pathlib import Path

import fitz


def encrypt_pdf(input_path: Path, password: str, output_path: Path) -> None:
    """Encrypt a PDF with a user/owner password using AES-256."""
    with fitz.open(input_path) as doc:
        doc.save(
            output_path,
            encryption=fitz.PDF_ENCRYPT_AES_256,
            user_pw=password,
            owner_pw=password,
        )

def decrypt_pdf(input_path: Path, password: str, output_path: Path) -> bool:
    """Decrypt a PDF using a password. Returns True if successful."""
    with fitz.open(input_path) as doc:
        if doc.is_encrypted:
            if not doc.authenticate(password):
                return False
        doc.save(output_path)
    return True

def redact_text(input_path: Path, text_to_redact: str, output_path: Path) -> int:
    """Redact specific text throughout the document. Returns count of redactions."""
    redaction_count = 0
    with fitz.open(input_path) as doc:
        for page in doc:
            text_instances = page.search_for(text_to_redact)
            for inst in text_instances:
                page.add_redact_annot(inst, fill=(0, 0, 0))  # Black box
                redaction_count += 1
            if text_instances:
                page.apply_redactions()
        doc.save(output_path)
    return redaction_count

def add_watermark_text(
    input_path: Path, 
    text: str, 
    output_path: Path, 
    opacity: float = 0.5,
    fontsize: int = 50,
    rotate: int = 0
) -> None:
    """Add a text watermark to every page of the PDF."""
    with fitz.open(input_path) as doc:
        for page in doc:
            # Calculate diagonal position roughly
            rect = page.rect
            # Insert text box centered and rotated
            page.insert_textbox(
                rect,
                text,
                fontsize=fontsize,
                color=(0.7, 0.7, 0.7),  # Gray
                rotate=rotate,
                align=fitz.TEXT_ALIGN_CENTER,
                fill_opacity=opacity
            )
        doc.save(output_path)
