# ManiPDF

**ManiPDF** is a robust, local, and privacy-first PDF manipulation suite. Designed for both power users via a rapid CLI and general users via a rich GUI, it ensures your sensitive documents never leave your machine.

## 🌟 Key Features

### ✅ Currently Available (Core, CLI & GUI)
- **Organization**: Merge, Split, Delete, Rotate, Extract, Sort, N-up (4-on-1, etc.), and Overlay (Stamping).
- **Security**: AES-256 Encryption, Decryption, Text Redaction (Black-boxing), and Text Watermarking.
- **Modification**: Find & Replace Text, Page Numbers, and PDF Compression.
- **Conversions**: 
    - **To PDF**: Images (JPG, PNG, etc.) and Office Documents (requires LibreOffice).
    - **From PDF**: Render pages to images and extract embedded images.
- **Advanced**: OCR Recognition (Searchable PDF), visual PDF Comparison, and Create Blank PDF.

### 🚧 In Development
- **Packaging**: Standalone executables for Linux/Windows/macOS via PyInstaller.
- **Visual Editing**: A real-time PDF viewer for direct page manipulation.

---

## 🛠 Installation

### Prerequisites
- **Python 3.12+**
- **LibreOffice** (Optional: required for Office-to-PDF conversions)
- **Tesseract OCR** (Optional: required for OCR features)

### Using `uv` (Recommended)
```bash
# Clone the repository
git clone https://github.com/CodingWithMK/manipdf_pdf-manipulation-tool.git
cd manipdf_pdf-manipulation-tool

# Install dependencies and create venv
uv sync
```

### Using `pip`
```bash
pip install .
```

### For Developers Using `pip`
```bash
pip install -e .
```

---

## 🚀 Quick Start Guide

### Command Line Interface
The CLI is the fastest way to manipulate PDFs. Use `uv run manipdf --help` for a full command list.

**Merge PDFs:**
```bash
uv run manipdf merge file1.pdf file2.pdf --output merged.pdf
```

**Encrypt a PDF:**
```bash
uv run manipdf encrypt private.pdf --output protected.pdf
```

**Add Page Numbers:**
```bash
uv run manipdf number input.pdf --output numbered.pdf
```

**Find and Replace Text:**
```bash
uv run manipdf edit-text input.pdf --search "Old Company" --replace "New Company" --output updated.pdf
```

**Convert Images to PDF:**
```bash
# Individual files
uv run manipdf to-pdf img1.jpg img2.png --output portfolio.pdf

# Entire directory of images
uv run manipdf to-pdf /path/to/images_folder --output gallery.pdf
```

**Apply OCR (Searchable PDF):**
```bash
uv run manipdf ocr input.pdf --output searchable.pdf
```

### Using Absolute Paths
You can use absolute paths to files located anywhere on your system. This is particularly useful when working with files in different directories.

**Example with Absolute Paths (macOS/Linux):**
```bash
uv run manipdf to-pdf \
  /Users/username/Downloads/photo1.jpg \
  /Users/username/Pictures/photo2.png \
  --output /Users/username/Documents/merged.pdf
```

### Graphical User Interface
To launch the experimental GUI:
```bash
uv run manipdf gui
```

---

## 🏗 Architecture
ManiPDF follows a **Core-Adapter** architecture:
- `src/manipdf/core/`: Agnostic business logic. Pure Python, no UI dependencies.
- `src/manipdf/cli/`: Typer-based adapter for terminal interaction.
- `src/manipdf/gui/`: PySide6-based adapter for desktop interaction.

This decoupling ensures the core logic is highly testable and can be integrated into other workflows easily.

## 🧪 Testing
We maintain a comprehensive suite of unit and integration tests.
```bash
export PYTHONPATH=$PYTHONPATH:src
uv run pytest
```
