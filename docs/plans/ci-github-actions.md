GitHub Actions: Build & Release (example)
========================================

This document contains an example GitHub Actions workflow for building ManiPDF on Windows and macOS and publishing installers as GitHub Release assets when a tag `v*` is pushed.

High level
----------
- Trigger: push tags (v*).
- Jobs: test, build-windows, build-macos (x86_64 & arm64), universalize-macos, release.

Important notes
---------------
- This is an example to copy into `.github/workflows/release.yml`. You must adapt paths to your repository, ensure `assets/icon.ico` and `assets/icon.icns` exist, and add any additional pip dependencies.
- The macOS universalization step assumes you produce two artifacts (x86_64 and arm64) and combine them with `lipo`.

Example YAML outline (conceptual)
---------------------------------
name: Build & Release

  push:
    tags:
      - 'v*'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with: python-version: '3.12'
      - name: Install deps
        run: |
          python -m pip install --upgrade pip
          pip install -e .
          pip install pytest
      - name: Run tests
        run: pytest -q

  build-windows:
    needs: test
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with: python-version: '3.12'
      - name: Install NSIS
        run: choco install nsis -y
      - name: Install deps and PyInstaller
        run: |
          python -m pip install --upgrade pip
          pip install . pyinstaller
      - name: Build with PyInstaller
        run: |
          echo "from manipdf.gui.main import main\nif __name__ == '__main__': main()" > run_gui.py
          pyinstaller --noconfirm --clean --name ManiPDF --onedir --windowed --icon=assets/icon.ico run_gui.py
      - name: Create NSIS installer
        run: |
          cp -r dist/ManiPDF build_installer/
          sed "s/\\${VERSION}/$GITHUB_REF_NAME/g" build/installer.nsi > build_installer/installer.nsi
          makensis build_installer/installer.nsi
      - uses: actions/upload-artifact@v4
        with:
          name: windows-installer
          path: ManiPDF-${{ github.ref_name }}-win-x64-setup.exe

  build-macos-x86_64:
    needs: test
    runs-on: macos-14
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with: python-version: '3.12'
      - name: Install deps and PyInstaller
        run: |
          python -m pip install --upgrade pip
          pip install . pyinstaller
      - name: Build amd64
        run: |
          echo "from manipdf.gui.main import main\nif __name__ == '__main__': main()" > run_gui.py
          pyinstaller --noconfirm --clean --name ManiPDF --onedir --windowed --icon=assets/icon.icns run_gui.py
          hdiutil create -srcfolder dist/ManiPDF -volname "ManiPDF-${{ github.ref_name }}-x86_64" -ov -format UDZO manipdf-${{ github.ref_name }}-macos-x86_64.dmg
      - uses: actions/upload-artifact@v4
        with:
          name: macos-x86_64-dmg
          path: manipdf-${{ github.ref_name }}-macos-x86_64.dmg

  build-macos-arm64:
    needs: test
    runs-on: macos-14
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with: python-version: '3.12'
      - name: Install deps and PyInstaller
        run: |
          python -m pip install --upgrade pip
          pip install . pyinstaller
      - name: Build arm64
        run: |
          echo "from manipdf.gui.main import main\nif __name__ == '__main__': main()" > run_gui.py
          pyinstaller --noconfirm --clean --name ManiPDF --onedir --windowed --icon=assets/icon.icns run_gui.py
          hdiutil create -srcfolder dist/ManiPDF -volname "ManiPDF-${{ github.ref_name }}-arm64" -ov -format UDZO manipdf-${{ github.ref_name }}-macos-arm64.dmg
      - uses: actions/upload-artifact@v4
        with:
          name: macos-arm64-dmg
          path: manipdf-${{ github.ref_name }}-macos-arm64.dmg

  universalize-macos:
    needs: [build-macos-x86_64, build-macos-arm64]
    runs-on: macos-14
    steps:
      - name: Download artifacts
        uses: actions/download-artifact@v4
        with:
          name: macos-x86_64-dmg
          path: ./artifacts/x86_64
      - name: Download arm64
        uses: actions/download-artifact@v4
        with:
          name: macos-arm64-dmg
          path: ./artifacts/arm64
      - name: Extract DMGs and lipo binaries
        run: |
          hdiutil attach artifacts/x86_64/manipdf-${{ github.ref_name }}-macos-x86_64.dmg -mountpoint /Volumes/ManiPDF-x86
          hdiutil attach artifacts/arm64/manipdf-${{ github.ref_name }}-macos-arm64.dmg -mountpoint /Volumes/ManiPDF-arm
          cp -r /Volumes/ManiPDF-x86/ManiPDF.app ./ManiPDF-x86.app
          cp -r /Volumes/ManiPDF-arm/ManiPDF.app ./ManiPDF-arm.app
          lipo -create -output ManiPDF-universal ./ManiPDF-x86.app/Contents/MacOS/ManiPDF ./ManiPDF-arm.app/Contents/MacOS/ManiPDF
          cp ManiPDF-universal ./ManiPDF-x86.app/Contents/MacOS/ManiPDF
          mv ManiPDF-x86.app ManiPDF.app
          hdiutil create -srcfolder ManiPDF.app -volname "ManiPDF-${{ github.ref_name }}" -ov -format UDZO ManiPDF-${{ github.ref_name }}-macos-universal.dmg
      - uses: actions/upload-artifact@v4
        with:
          name: macos-universal-dmg
          path: ManiPDF-${{ github.ref_name }}-macos-universal.dmg

  release:
    needs: [build-windows, universalize-macos]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Download windows artifact
        uses: actions/download-artifact@v4
        with:
          name: windows-installer
          path: ./release
      - name: Download mac artifact
        uses: actions/download-artifact@v4
        with:
          name: macos-universal-dmg
          path: ./release
      - name: Create release
        uses: actions/create-release@v1
        with:
          tag_name: ${{ github.ref_name }}
          release_name: Release ${{ github.ref_name }}
          body: |
            See attached installers for Windows and macOS.
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      - name: Upload windows
        uses: softprops/action-upload-release-asset@v1
        with:
          upload_url: ${{ steps.create_release.outputs.upload_url }}
          asset_path: ./release/ManiPDF-${{ github.ref_name }}-win-x64-setup.exe
          asset_name: ManiPDF-${{ github.ref_name }}-win-x64-setup.exe
          asset_content_type: application/octet-stream
      - name: Upload mac
        uses: softprops/action-upload-release-asset@v1
        with:
          upload_url: ${{ steps.create_release.outputs.upload_url }}
          asset_path: ./release/ManiPDF-${{ github.ref_name }}-macos-universal.dmg
          asset_name: ManiPDF-${{ github.ref_name }}-macos-universal.dmg
          asset_content_type: application/x-apple-diskimage

This file is conceptual and intended to be adapted to the repo. The exact paths and commands should be tested locally on the target OS prior to relying on the workflow.
