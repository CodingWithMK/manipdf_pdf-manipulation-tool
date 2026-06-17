Windows NSIS Packaging Plan
===========================

Overview
--------
This document explains how to build ManiPDF on Windows using PyInstaller and then package it into an NSIS installer. The installer will include both the GUI executable and the CLI script, create Start Menu and Desktop shortcuts, and install the CLI into a folder added to the user's PATH (optionally via a small wrapper exe).

File layout produced by PyInstaller (`--onedir`):

dist/ManiPDF/
  ManiPDF.exe               # GUI executable created by PyInstaller
  manipdf.exe               # CLI wrapper (console) or manipdf console script
  python39.dll              # Python runtime (example)
  all required PySide6 libs
  PySide6/Qt/plugins/...

NSIS installer goals
- Install files to %LOCALAPPDATA%\Programs\ManiPDF\
- Install a CLI wrapper to %LOCALAPPDATA%\Programs\ManiPDF\bin\manipdf.exe and add that `bin` to PATH for the current user (or create a shim in %USERPROFILE%\AppData\Local\Microsoft\WindowsApps)
- Create Start Menu shortcuts and optional Desktop shortcut
- Add an uninstaller entry in Windows Control Panel
- Create a single .exe installer: ManiPDF-<version>-win-x64-setup.exe

Tools required (CI & local):
- Python 3.12
- pip install pyinstaller
- NSIS (makensis)

Suggested NSIS script (example snippet)
---------------------------------------
Create `build/installer.nsi` in your repo or generate it in CI. Replace ${VERSION} and paths accordingly.

;-------------- installer.nsi ----------------
!define APP_NAME "ManiPDF"
!define APP_EXE "ManiPDF.exe"
!define VERSION "${VERSION}"
!define INSTALL_DIR "$LOCALAPPDATA\Programs\${APP_NAME}"
!define BIN_DIR "${INSTALL_DIR}\bin"

OutFile "${APP_NAME}-${VERSION}-win-x64-setup.exe"
InstallDir "$LOCALAPPDATA\Programs\${APP_NAME}"
RequestExecutionLevel user

Section "Install"
  SetOutPath "$INSTDIR"
  File /r "dist\ManiPDF\*"
  ; create bin
  CreateDirectory "$INSTDIR\bin"
  ; copy/rename CLI console exe
  File "dist\ManiPDF\manipdf.exe"
  ; write uninstall
  WriteUninstaller "$INSTDIR\Uninstall.exe"
  ; create Start Menu shortcuts
  CreateDirectory "$SMPROGRAMS\${APP_NAME}"
  CreateShortCut "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk" "$INSTDIR\${APP_EXE}"
  ; optional Desktop shortcut
  CreateShortCut "$DESKTOP\${APP_NAME}.lnk" "$INSTDIR\${APP_EXE}"
  ; add CLI to user PATH (append to HKCU environment)
  ReadRegStr $R0 HKCU "Environment" "Path"
  StrCmp $R0 "" +2
  StrCpy $R0 "$R0;${BIN_DIR}"
  WriteRegStr HKCU "Environment" "Path" "$R0"
SectionEnd

Section "Uninstall"
  Delete "$INSTDIR\${APP_EXE}"
  RMDir /r "$INSTDIR"
  Delete "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk"
  RMDir "$SMPROGRAMS\${APP_NAME}"
  ; Note: PATH cleanup can be complex—consider leaving PATH unchanged or removing only the exact bin path you added.
SectionEnd

;-------------------------------------------------

CI job snippet
--------------
This is the core build step inside the `build-windows` job in GitHub Actions:

- name: Install NSIS
  uses: actions-rs/nsistool@v2   # or use choco to install NSIS

- name: Build with PyInstaller
  run: |
    python -m pip install --upgrade pip
    pip install . pyinstaller
    echo "from manipdf.gui.main import main\nif __name__ == '__main__': main()" > run_gui.py
    pyinstaller --noconfirm --clean --name ManiPDF --onedir --windowed --icon=assets/icon.ico run_gui.py

- name: Create NSIS installer
  run: |
    mkdir -p installer_build
    cp -r dist/ManiPDF/* installer_build/
    cp build/installer.nsi installer_build/installer.nsi
    sed -i "s/\${VERSION}/$GITHUB_REF_NAME/g" installer_build/installer.nsi
    makensis installer_build/installer.nsi

Testing locally
--------------
Test the produced NSIS installer on a clean Windows VM (or real machine) to verify:
- Shortcuts created and working
- CLI is available through a new console or after re-login (PATH changes affect new shells)
- Uninstall works and removes files

Notes and pitfalls
------------------
- PATH modification: modifying HKCU environment PATH requires the user to log out or start a new shell to see the change. Consider creating a shortcut that runs the CLI from the installed folder.
- If you prefer not to modify PATH, place a shim at `%LOCALAPPDATA%\Microsoft\WindowsApps` which is already in user PATH on modern Windows, but requires special handling.
- NSIS script will likely need tweaks for localization and edge-cases.
