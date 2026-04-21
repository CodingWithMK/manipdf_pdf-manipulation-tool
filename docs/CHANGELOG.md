# Changelog

All notable changes to this project will be documented in this file.

## [0.1.0] - 2026-04-13

### Added
- **Recursive Directory Support**: The `to-pdf` command now automatically expands directories to collect and sort image files.
- **Local OCR Support**: Integrated `pytesseract` for searchable PDF generation in the Advanced module.
- **Find & Replace**: Implemented `edit-text` command for local text manipulation within PDFs.
- **CLI Robustness**: Added explicit file existence validation across all 15+ CLI commands with clear error reporting.
- **Extended Testing**: Increased test suite to 28+ tests, including new `test_cli.py` and `test_advanced.py`.
- **Phase 5 Planning**: Published an extensive GUI implementation plan with modern red-accented design and asynchronous architecture.

### Changed
- **Strict Locality Enforcement**: Removed `playwright` dependency and Web-to-PDF functionality to ensure 100% offline operation.
- **Documentation**: Revamped `README.md` with absolute path examples and directory conversion guides.
- **CLI Polish**: Added `Rich` status indicators to all organization and modification commands.

### Fixed
- Resolved `AttributeError` in the core redaction logic (`add_redact_annot`).

### Planned
- **Phase 5**: Implement `PySide6` GUI with dynamic System/Light/Dark themes and red-accent navigation.
- **Phase 5**: Connect all core modules to GUI panels using a non-blocking `QThread` worker pattern.
- **Phase 6**: Cross-platform distribution using `PyInstaller`.
