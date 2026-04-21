import pytest
from typer.testing import CliRunner
from manipdf.cli.main import app
from pathlib import Path
import fitz

runner = CliRunner()

def test_cli_merge(sample_pdf: Path, another_pdf: Path, tmp_path: Path):
    output = tmp_path / "cli_merged.pdf"
    result = runner.invoke(app, ["merge", str(sample_pdf), str(another_pdf), "--output", str(output)])
    assert result.exit_code == 0
    assert output.exists()
    with fitz.open(output) as doc:
        assert len(doc) == 4

def test_cli_split(sample_pdf: Path, tmp_path: Path):
    output_dir = tmp_path / "cli_split"
    result = runner.invoke(app, ["split", str(sample_pdf), "--output-dir", str(output_dir)])
    assert result.exit_code == 0
    assert len(list(output_dir.glob("*.pdf"))) == 3

def test_cli_delete(sample_pdf: Path, tmp_path: Path):
    output = tmp_path / "cli_deleted.pdf"
    result = runner.invoke(app, ["delete", str(sample_pdf), "--pages", "0", "--output", str(output)])
    assert result.exit_code == 0
    with fitz.open(output) as doc:
        assert len(doc) == 2

def test_cli_encrypt_decrypt(sample_pdf: Path, tmp_path: Path):
    encrypted = tmp_path / "cli_encrypted.pdf"
    # Note: typer runner handles input for prompt if needed, but here we pass password via option or let it prompt
    # Since we added password prompt=True, we might need to provide input
    result = runner.invoke(app, ["encrypt", str(sample_pdf), "--output", str(encrypted)], input="password\npassword\n")
    assert result.exit_code == 0
    
    decrypted = tmp_path / "cli_decrypted.pdf"
    result = runner.invoke(app, ["decrypt", str(encrypted), "--output", str(decrypted)], input="password\n")
    assert result.exit_code == 0
    assert decrypted.exists()

def test_cli_to_pdf_directory(tmp_path: Path):
    img_dir = tmp_path / "images"
    img_dir.mkdir()
    from PIL import Image
    Image.new("RGB", (100, 100), color="red").save(img_dir / "1.jpg")
    Image.new("RGB", (100, 100), color="blue").save(img_dir / "2.png")
    
    output = tmp_path / "cli_dir.pdf"
    result = runner.invoke(app, ["to-pdf", str(img_dir), "--output", str(output)])
    assert result.exit_code == 0
    assert output.exists()
    with fitz.open(output) as doc:
        assert len(doc) == 2

def test_cli_sort(sample_pdf: Path, tmp_path: Path):
    output = tmp_path / "cli_sorted.pdf"
    result = runner.invoke(app, ["sort", str(sample_pdf), "--order", "2,1,0", "--output", str(output)])
    assert result.exit_code == 0
    with fitz.open(output) as doc:
        assert doc[0].get_text().strip() == "Page 3"

def test_cli_edit_text(sample_pdf: Path, tmp_path: Path):
    output = tmp_path / "cli_edited.pdf"
    result = runner.invoke(app, ["edit-text", str(sample_pdf), "--search", "Page", "--replace", "Leaf", "--output", str(output)])
    assert result.exit_code == 0
    with fitz.open(output) as doc:
        assert "Leaf" in doc[0].get_text()
