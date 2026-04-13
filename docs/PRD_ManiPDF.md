# **📄 Product Requirements Document: ManiPDF**

**Vision:** To provide a robust, completely local, privacy-first PDF manipulation suite that offers both rapid CLI execution for power users and a rich GUI for visual editing.

## **1\. Product Overview**

### **1.1 Problem Statement**

Users frequently need to manipulate, convert, and edit PDFs. However, most available tools are either expensive enterprise solutions (like Adobe Acrobat) or cloud-based freemium services that compromise user privacy by requiring sensitive document uploads.

### **1.2 Value Proposition**

ManiPDF is a 100% offline, fully self-contained desktop application. It guarantees data privacy while delivering a comprehensive suite of PDF tools mirroring popular cloud services, accessible via a seamless Graphical User Interface (GUI) or a scriptable Command Line Interface (CLI).

### **1.3 Feature Requirements**

Based on the provided specifications, features are categorized as follows:

| Feature Category | Tools / Capabilities | Interface |
| :---- | :---- | :---- |
| **Organization** | Merge, Split, Delete/Rotate/Extract/Sort Pages, N-up, Overlay | GUI & CLI |
| **Security** | Encrypt/Decrypt, Redact (Schwärzen), Watermark | GUI & CLI |
| **Modification** | Edit Text/Images, Page Numbers, Compress/Optimize | GUI & CLI |
| **Conversions (To PDF)** | Word, PPT, Excel, Images (JPG/PNG), Website | GUI & CLI |
| **Conversions (From PDF)** | PDF to Images, Extract Images | GUI & CLI |
| **Advanced** | OCR Recognition, Compare PDFs, Create Blank PDF | GUI & CLI |

## **2\. System Architecture**

### **2.1 Tech Stack**

* **Language:** Python 3.10+  
* **Environment Management:** uv  
* **CLI Framework:** Typer  
* **GUI Framework:** PySide6 (Chosen for its robust QGraphicsView for PDF rendering)  
* **Core PDF Engines:** \- PyMuPDF (fitz) for rendering/compression  
  * pypdf for structural manipulation  
  * pytesseract for OCR  
* **Conversions:** Headless LibreOffice (Office docs) & Playwright (Web)

### **2.2 Architecture Diagrams**

#### **System Component Flow**

graph TD  
    User(\[User\])  
    CLI\[Typer CLI Adapter\]  
    GUI\[PySide6 GUI Adapter\]  
    Core\[ManiPDF Core Logic Layer\]  
    PyMuPDF\[PyMuPDF Engine\]  
    Pypdf\[pypdf Engine\]  
    ExtDeps\[External Dependencies\]  
      
    User \--\>|Terminal Commands| CLI  
    User \--\>|Mouse/Keyboard Interactions| GUI  
    CLI \--\>|Data Transfer Objects| Core  
    GUI \--\>|Data Transfer Objects| Core  
      
    Core \--\>|Render/Extract/Redact| PyMuPDF  
    Core \--\>|Merge/Split/Encrypt| Pypdf  
    Core \--\>|System Calls| ExtDeps  
      
    subgraph External Dependencies  
        Tesseract\[Tesseract OCR\]  
        LibreOffice\[LibreOffice Headless\]  
    end

## **3\. Implementation Strategy**

### **3.1 Project Setup with uv**

```bash
\# Initialize and add dependencies  
uv init manipdf  
uv add typer pypdf pymupdf pillow pdf2image PySide6  
uv add \--dev pytest pyinstaller
```

### **3.2 Directory Structure**

```
manipdf/  
├── src/  
│   ├── manipdf/  
│   │   ├── \_\_init\_\_.py  
│   │   ├── core/              \# Agnostic PDF manipulation logic  
│   │   │   ├── merger.py  
│   │   │   ├── compressor.py  
│   │   │   └── security.py  
│   │   ├── cli/               \# Typer CLI adapter  
│   │   │   └── main.py  
│   │   ├── gui/               \# PySide6 GUI adapter  
│   │   │   ├── app.py  
│   │   │   └── components/  
│   └── main.py                \# Entry point router  
├── pyproject.toml  
└── README.md
```

### **3.3 Critical Code Snippets**

#### **Core Logic: Compression (PyMuPDF)**

```python
import fitz  \# PyMuPDF  
import os

def compress\_pdf(input\_path: str, output\_path: str) \-\> dict:  
    original\_size \= os.path.getsize(input\_path)  
    try:  
        doc \= fitz.open(input\_path)  
        doc.save(  
            output\_path,  
            garbage=4,          \# High-level garbage collection  
            deflate=True,       \# Compress streams  
            clean=True          \# Sanitize contents  
        )  
        doc.close()  
        new\_size \= os.path.getsize(output\_path)  
        return {"reduction": round((1 \- (new\_size / original\_size)) \* 100, 2)}  
    except Exception as e:  
        raise RuntimeError(f"Compression failed: {e}")
```

#### **CLI Adapter (Typer)**

```python
import typer  
from manipdf.core.compressor import compress\_pdf

app \= typer.Typer()

@app.command()  
def compress(input\_file: str, output\_file: str \= "compressed.pdf"):  
    """Command-line interface for PDF compression."""  
    typer.echo(f"Processing {input\_file}...")  
    result \= compress\_pdf(input\_file, output\_file)  
    typer.echo(f"Success\! Reduced by {result\['reduction'\]}%")
```

#### **Application Entry Point**

```python
import sys

def main():  
    \# If arguments exist, run CLI; otherwise, launch GUI  
    if len(sys.argv) \> 1:  
        from manipdf.cli.main import app  
        app()  
    else:  
        from PySide6.QtWidgets import QApplication  
        from manipdf.gui.app import MainWindow  
        app\_inst \= QApplication(sys.argv)  
        window \= MainWindow()  
        window.show()  
        sys.exit(app\_inst.exec())
```

## **4\. Packaging & Distribution**

**Tool:** PyInstaller (--onedir mode recommended for Qt performance).  
**System Dependency Check:**  
On startup, ManiPDF checks for tesseract and libreoffice in the system path. If missing, GUI features requiring them (OCR, Office-to-PDF) are disabled with a descriptive tooltip.  
uv run pyinstaller \--noconfirm \--onedir \--windowed \--name "ManiPDF" src/main.py  
