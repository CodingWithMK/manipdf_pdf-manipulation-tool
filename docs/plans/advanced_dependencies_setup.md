# ManiPDF Advanced Dependencies: Installation & Integration Guide

To enable **OCR Recognition** and **Office-to-PDF Conversion**, ManiPDF requires two external system engines. Following our **100% local** architecture, these engines run entirely on your machine without cloud dependencies.

---

## 1. Tesseract OCR
Used for making scanned PDFs searchable by analyzing images and extracting text.

### Installation

#### macOS
```bash
brew install tesseract
brew install tesseract-lang # Optional: for multi-language support
```

#### Windows
1. Download the installer from the [UB Mannheim Tesseract Wiki](https://github.com/UB-Mannheim/tesseract/wiki).
2. Install to the default path (e.g., `C:\Program Files\Tesseract-OCR`).
3. **Critical**: Add this path to your System **PATH** environment variable.
4. Verify in a new terminal: `tesseract --version`

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install tesseract-ocr
# Install specific languages
sudo apt install tesseract-ocr-eng tesseract-ocr-deu
```

### Integration Details
ManiPDF uses the `pytesseract` library, which acts as a wrapper for the `tesseract` binary. It looks for the binary in your system PATH. If you have a custom installation path, you can define it in your shell profile:
```bash
export TESSDATA_PREFIX=/path/to/tessdata
```

---

## 2. LibreOffice
Used for high-fidelity conversion of `.docx`, `.xlsx`, and `.pptx` files to PDF.

### Installation

#### macOS
```bash
brew install --cask libreoffice
```
**Path Setup**: LibreOffice on macOS is installed as an App. To use it in the CLI/GUI, add the binary to your path:
```bash
export PATH="/Applications/LibreOffice.app/Contents/MacOS:$PATH"
```

#### Windows
1. Download from [libreoffice.org](https://www.libreoffice.org/download/download/).
2. Add the `program` folder (e.g., `C:\Program Files\LibreOffice\program`) to your System **PATH**.
3. Verify in CMD: `soffice --version`

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install libreoffice-writer libreoffice-calc libreoffice-impress
```

### Integration Details
ManiPDF integrates LibreOffice via a **headless subprocess**. When you trigger an Office conversion, ManiPDF executes:
```bash
soffice --headless --convert-to pdf --outdir [output_dir] [input_file]
```
This ensures that the document is rendered exactly as it would appear in the office suite, entirely offline.

---

## 🚀 Final Verification in ManiPDF

Once installed, restart ManiPDF. 
1.  **For OCR**: Go to `Advanced > OCR`, drop a scanned image-based PDF, and click **Run OCR**.
2.  **For Office**: Go to `Conversions > To PDF`, drop a `.docx` file, and click **Convert**.

If the dependencies are missing, the GUI will now display a **Red Toast Notification** detailing the missing binary.
