from pathlib import Path

import fitz

from manipdf.core.security import (
    add_watermark_text,
    decrypt_pdf,
    encrypt_pdf,
    redact_text,
)


def test_encryption_decryption(sample_pdf: Path, tmp_path: Path) -> None:
    encrypted = tmp_path / "encrypted.pdf"
    decrypted = tmp_path / "decrypted.pdf"
    password = "secret_password"
    
    encrypt_pdf(sample_pdf, password, encrypted)
    assert encrypted.exists()
    
    # Verify encrypted
    with fitz.open(encrypted) as doc:
        assert doc.needs_pass
        
    # Decrypt
    success = decrypt_pdf(encrypted, password, decrypted)
    assert success
    assert decrypted.exists()
    
    # Verify decrypted
    with fitz.open(decrypted) as doc:
        assert not doc.needs_pass
        assert len(doc) == 3

def test_redact_text(sample_pdf: Path, tmp_path: Path) -> None:
    output = tmp_path / "redacted.pdf"
    # sample_pdf contains "Page 1", "Page 2", "Page 3"
    count = redact_text(sample_pdf, "Page 2", output)
    assert count == 1
    with fitz.open(output) as doc:
        # Verify page 2 is redacted (it applies black boxes)
        # We search for it again, should not be found if apply_redactions worked
        assert not doc[1].search_for("Page 2")

def test_add_watermark_text(sample_pdf: Path, tmp_path: Path) -> None:
    output = tmp_path / "watermarked.pdf"
    add_watermark_text(sample_pdf, "CONFIDENTIAL", output)
    assert output.exists()
    with fitz.open(output) as doc:
        # Check if watermark text exists on first page
        assert "CONFIDENTIAL" in doc[0].get_text()
