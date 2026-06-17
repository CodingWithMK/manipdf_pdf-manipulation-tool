ManiPDF Release Plan
====================

Goal
----
Produce distributable installers for ManiPDF that include both the GUI and CLI:

- Windows: NSIS installer (unsigned)
- macOS: universal DMG containing a .app (unsigned, not notarized)

All builds are produced automatically by GitHub Actions when a Git tag like `v0.2.0` is pushed. The CI will run tests, build PyInstaller onedir outputs, create OS-specific installers, and attach them to a GitHub Release.

Phases
------
1. Pre-flight (local)
   - Add a tiny run script for the GUI entrypoint (run_gui.py).
   - Add a small CLI wrapper to expose the CLI entrypoint as `manipdf` when installed (pyproject already has a console script configured).
   - Add application icons: .ico (windows) and .icns (macos). Place them at `assets/icon.ico` and `assets/icon.icns`.
   - Add LICENSE file if missing and ensure README lists external dependencies (Tesseract, LibreOffice).

2. Local packaging (verification)
   - Create a clean virtualenv on each platform and install the package and PyInstaller.
   - Build with PyInstaller in `--onedir --windowed` mode.
   - Manually test the onedir binary on a clean VM to ensure Qt and plugins are present.

3. Installer creation
   - Windows: Use NSIS to create an installer from the PyInstaller onedir output. Include Start Menu and optionally Desktop shortcuts. Add an option to install CLI into a user-writable location (`%LOCALAPPDATA%\Programs\ManiPDF\`), and add `manipdf.exe` wrapper to `%LOCALAPPDATA%\Programs\ManiPDF\bin\`.
   - macOS: Create a signed (if you have keys) or unsigned .app from the PyInstaller onedir; then create a DMG including an Applications symlink and the app (universal binary built on macOS universal runner).

4. CI automation
   - GitHub Actions triggered on tag push `v*`.
   - Jobs: test -> build-windows -> build-macos -> release.
   - build-windows uses `windows-latest`, installs Python, dependencies, PyInstaller, NSIS, builds onedir, runs makensis with a generated installer script, uploads artifact.
   - build-macos uses `macos-14` runner, installs Python, builds universal2 wheels (if needed), builds onedir, packages .app, creates DMG, uploads artifact.
   - release job collects artifacts and uses `actions/create-release` to publish assets. Also create SHA256SUMS.

5. Post-release verification
   - Download installer artifacts from the release and test on clean environments (Windows 10/11, macOS Ventura/Monterey/12+ with Intel and Apple Silicon if available).

Decisions and rationale
-----------------------
- Use `onedir` (instead of `onefile`) because PySide6/Qt apps are easier to debug and more reliable when their plugin folder structure remains intact.
- Build both GUI and CLI into the same artifact. The GUI binary is the primary entrypoint, and the CLI is the installed console script that maps to `manipdf.cli.main:app` defined in `pyproject.toml`.
- Start with unsigned artifacts. Notarization and code signing are recommended but require paid developer accounts and key management.
- Create universal macOS binaries by using `macos-latest` runner (which may provide universal2 Python already) and passing PyInstaller options to include both architectures if possible. Alternatively, build separate x86_64 and arm64 runs and lipo them together.

Risks and mitigations
---------------------
- Missing Qt plugin: add explicit `--add-data` entries in PyInstaller .spec file or include a runtime hook to collect them.
- External native dependencies (Tesseract/LibreOffice): detect at runtime and show helpful error messages; document installation steps in README.
- CI runner environment differences: test builds locally in clean VMs before relying on CI.

What you will find in this folder
---------------------------------
- windows-nsis.md: Step-by-step Windows build instructions, example NSIS script, and GitHub Actions job snippet.
- macos-dmg.md: Step-by-step macOS build instructions, DMG creation details, universal binary guidance, and CI job snippet.
- ci-github-actions.md: Full example GitHub Actions YAML with jobs for test, windows build, macos build, and release.
- pyinstaller-spec.md: Example .spec snippets, collection of PySide6 files, and troubleshooting tips.
- checklist.md: Final release checklist you can use before tagging and after the release.
