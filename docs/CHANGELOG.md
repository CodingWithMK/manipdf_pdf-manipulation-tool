# Changelog

All notable changes to this project will be documented in this file.

## [0.2.0] - 2026-06-17

### Added
- **Extract Pages as Separate PDFs**: New feature in both CLI and GUI to extract specified pages as individual PDF files (one per page) with automatic zero-padded naming (e.g., `document_p001.pdf`, `document_p002.pdf`).
- **CLI**: Added `--extract-as-separate` / `-s` flag and `--output-dir` / `-d` option to `extract` command.
- **GUI**: Added checkbox "Extract each page as separate PDF file" with descriptive tooltip in the Selective Extract tab; prompts for output folder when enabled.
- **Core**: New `extract_pages_as_separate_pdfs()` function in `organization.py organization module with comprehensive test coverage (5 test cases including edge cases).

### Changed
- Updated version to 0.2.0 across all configuration files.

## [0.1.0] - 2026-04-13

### Added
- **GUI Application**: Launched a modern PySide6-based desktop interface with a sleek red-accented design and categorical sidebar navigation.
- **Asynchronous UI Engine**: Implemented non-blocking PDF processing using a centralized `QThreadPool` and `QRunnable` worker architecture.
- **Dynamic Theming**: Added support for System, Light, and Dark themes with seamless live switching.
- **Enhanced UX Elements**: Integrated transparent toast notifications (green for success, red for error), drag-and-drop animations, and loading states for all action buttons.
- **System Integration**: Registered professional ManiPDF branding for the system Dock/Taskbar and implemented rounded corners for the sidebar logo.
- **Recursive Directory Support**: The `to-pdf` command now automatically expands directories to collect and sort image files (CLI & GUI).
- **Local OCR Support**: Integrated `pytesseract` for searchable PDF generation in the Advanced module.
- **Find & Replace**: Implemented `edit-text` command for local text manipulation within PDFs.
- **CLI Robustness**: Added explicit file existence validation across all 15+ CLI commands with clear error reporting.
- **Comprehensive Testing**: Expanded test suite to 35+ tests, including new `test_gui.py`, `test_cli.py`, and `test_advanced.py`.

### Changed
- **Architecture Refinement**: Transitioned GUI state management to a centralized `run_task` pattern for guaranteed UI cleanup and error recovery.
- **Strict Locality Enforcement**: Removed `playwright` dependency to ensure 100% offline operation.
- **Visual Polish**: Improved contrast in Light Mode for descriptions, instructions, and placeholders.
- **Documentation**: Revamped `README.md` with absolute path examples and directory conversion guides.

### Fixed
- Resolved `SyntaxError` caused by incorrect semicolon-based compound statements in the GUI.
- Fixed `TypeError` in background workers by decoupling functional arguments from GUI context metadata.
- Corrected launch-state bug where the pointing hand cursor was inactive until the first interaction.
- Restored missing `QComboBox` arrows and visibility of dropdown items in Light Mode.
- Resolved `AttributeError` in the core redaction logic (`add_redact_annot`).

### Planned
- **Phase 6**: Cross-platform distribution using `PyInstaller`.
- **UI Enhancements**: Implement a `QGraphicsView` based PDF viewer component for visual editing.
