# Changelog

All notable changes to this project will be documented in this file.

## [0.1.0] - 2026-04-13

### Added
- **Project Scaffolding**: Initialized with `uv`, directory structure established (`core`, `cli`, `gui`).
- **Core Organization Module**: Implemented `merge`, `split`, `delete`, `rotate`, `extract`, `sort`, `n-up`, and `overlay`.
- **Core Security Module**: Implemented `encrypt`, `decrypt`, `redact`, and `watermark`.
- **Core Modification Module**: Implemented `add_page_numbers` and `compress_pdf`.
- **Core Conversions Module**: Implemented `images_to_pdf`, `pdf_to_images`, `extract_images_from_pdf`, and `office_to_pdf`.
- **Core Advanced Module**: Implemented `create_blank_pdf` and `compare_pdfs`.
- **CLI Adapter**: Fully functional `Typer` CLI with 15+ commands and `Rich` progress indicators.
- **GUI Adapter**: Initial scaffolding for `PySide6` interface with sidebar navigation.
- **Testing**: 15 unit tests covering core logic across all modules.

### Changed
- Consolidated CLI and GUI entry points into a single `manipdf` command. 
- The GUI can now be launched via `manipdf gui`.
- Refactored `add_page_numbers` to use `insert_textbox` for better alignment control.
- Updated `ruff` configuration to ignore `B008` (Typer parameter pattern).

### Planned
- **Phase 5**: Complete the `PySide6` GUI panels for all core tools.
- **Phase 5**: Implement a `QGraphicsView` based PDF viewer component for visual editing.
- **Phase 6**: Implement `PyInstaller` build scripts for cross-platform distribution.
- **Advanced**: Integrate `pytesseract` for high-quality OCR support.
- **Conversions**: Integrate `playwright` for website-to-PDF functionality.
