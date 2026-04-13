# Master Implementation Plan: ManiPDF

## Architectural Guidelines
*   **Clean Architecture (Core-Adapter):** The `src/manipdf/core/` modules must be completely isolated from CLI (`Typer`) and GUI (`PySide6`) dependencies. They will expose pure Python functions/classes that accept standard data structures and return results or raise specific exceptions.
*   **Performance & Risk Mitigation:**
    *   **Large PDFs:** Use `PyMuPDF` (fitz) generators or iterative processing where possible to avoid loading entire 1000+ page PDFs into memory.
    *   **Thread-blocking:** GUI adapters will use `QThread` and `QRunnable` for any core calls to prevent freezing. External subprocesses (like LibreOffice) will be executed asynchronously.
*   **Testing Strategy:** `pytest` will be used to thoroughly test `core/` logic before adapter implementation. Mocking will be used for external dependencies (like LibreOffice or Playwright).

## Phases

### Phase 1: Environment Setup, Dependency Management, and Project Scaffolding
*   Initialize `uv` project (`uv init manipdf`).
*   Define dependencies in `pyproject.toml` (`PyMuPDF`, `pypdf`, `pytesseract`, `pdf2image`, `Pillow`, `typer`, `PySide6`, `pytest`).
*   Set up directory structure (`src/manipdf/core`, `src/manipdf/cli`, `src/manipdf/gui`, `tests/`).
*   Configure linting and formatting (e.g., `ruff`, `mypy`).
*   Create basic entry points for CLI and GUI (unified 'manipdf' command).

### Phase 2: Core Logic Implementation
*   Implement PDF Organization module (Merge, Split, Delete, Rotate, Extract, Sort, N-up, Overlay).
*   Implement PDF Security module (Encrypt, Decrypt, Redact, Watermark).
*   Implement PDF Modification module (Edit Text/Images, Page Numbers, Compress/Optimize).
*   Implement Conversions TO PDF module (Word, PPT, Excel via LibreOffice subprocess; Images; Website via Playwright).
*   Implement Conversions FROM PDF module (PDF to Images, Extract Images).
*   Implement Advanced module (OCR Recognition via pytesseract, Compare PDFs, Create Blank PDF).

### Phase 3: Core Logic Unit Testing
*   Write unit tests for Organization module.
*   Write unit tests for Security module.
*   Write unit tests for Modification module.
*   Write unit tests (with mocks) for Conversion modules.
*   Write unit tests for Advanced modules.
*   Ensure test coverage meets project standards.

### Phase 4: CLI Adapter Layer Integration
*   Initialize `Typer` app in `src/manipdf/cli/`.
*   Create CLI commands for Organization features mapping to `core`.
*   Create CLI commands for Security features.
*   Create CLI commands for Modification features.
*   Create CLI commands for Conversions and Advanced features.
*   Add progress bars (e.g., via `rich`) for long-running CLI tasks.

### Phase 5: GUI Adapter Layer Integration
*   Initialize `PySide6` application in `src/manipdf/gui/`.
*   Design main window layout (sidebar for categories, main area for tools).
*   Implement `QGraphicsView` based PDF viewer component.
*   Create UI panels for Organization, Security, and Modification features.
*   Wire UI actions to `core` logic using `QThread` to prevent UI blocking.
*   Implement progress indicators and error handling dialogs.

### Phase 6: PyInstaller Packaging and System Dependency Checks
*   Create `PyInstaller` spec file.
*   Handle hidden imports and resource paths for `PySide6` and `PyMuPDF`.
*   Implement runtime checks for external dependencies (LibreOffice, Tesseract).
*   Build and test standalone executables for the target OS (Linux).
*   Final QA and release preparation.
