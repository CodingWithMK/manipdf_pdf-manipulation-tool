macOS DMG Packaging Plan (Universal)
===================================

Goal
----
Create a universal macOS DMG that contains ManiPDF.app. The DMG will be unsigned and not notarized for the initial release. The DMG should be user-friendly (drag to Applications) and include a versioned filename: `ManiPDF-<version>-macos-universal.dmg`.

Strategy
--------
1. Build a universal Python environment on the macOS runner. There are two approaches:
   - Build two onedir outputs (x86_64 and arm64) on their respective runners, then use `lipo` to combine native binaries into a universal binary inside the .app. This is the most robust universal approach.
   - Alternatively, some GitHub runners provide universal-compatible Python; test whether a single build produces universal binaries. If not, use the two-build method.

2. Use PyInstaller `--onedir` to collect runtime files into a single folder structure. Convert that folder into an `.app` bundle structure: `MyApp.app/Contents/MacOS/MyApp` (executable) and `Resources` for icons and other resources.

3. Create a DMG using `hdiutil` with a custom volume name and a symlink to `/Applications` to allow users to drag the .app into Applications.

Detailed steps
--------------
1. Prepare build script (run on macos-latest):

   - Create run_gui.py
     echo "from manipdf.gui.main import main\nif __name__ == '__main__': main()" > run_gui.py

   - Install dependencies
     python -m pip install --upgrade pip
     pip install . pyinstaller

   - Build with PyInstaller
     pyinstaller --noconfirm --clean --name ManiPDF --onedir --windowed --icon=assets/icon.icns run_gui.py

2. Create the .app structure (example):

   mkdir -p ManiPDF.app/Contents/MacOS
   cp -r dist/ManiPDF/* ManiPDF.app/Contents/MacOS/
   cp assets/icon.icns ManiPDF.app/Contents/Resources/app.icns
   # Create an Info.plist
   cat > ManiPDF.app/Contents/Info.plist <<EOF
   <?xml version="1.0" encoding="UTF-8"?>
   <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
   <plist version="1.0">
   <dict>
     <key>CFBundleName</key><string>ManiPDF</string>
     <key>CFBundleDisplayName</key><string>ManiPDF</string>
     <key>CFBundleExecutable</key><string>ManiPDF</string>
     <key>CFBundleIdentifier</key><string>com.example.manipdf</string>
     <key>CFBundleVersion</key><string>${VERSION}</string>
     <key>CFBundleIconFile</key><string>app.icns</string>
     <key>LSApplicationCategoryType</key><string>public.app-category.productivity</string>
   </dict>
   </plist>
   EOF

3. Make the executable bit set
   chmod +x ManiPDF.app/Contents/MacOS/ManiPDF

4. Create DMG
   TEMP_DMG="manipdf-${VERSION}-temp.dmg"
   FINAL_DMG="ManiPDF-${VERSION}-macos-universal.dmg"
   hdiutil create -srcfolder ManiPDF.app -volname "ManiPDF ${VERSION}" -ov -format UDZO "$FINAL_DMG"

Universal binary strategy
------------------------
- Preferred: Build both arm64 and x86_64 versions separately and merge the Mach-O binaries with `lipo`.
- Steps:
  1. Build on macos-12 (or appropriate runners) for x86_64 and arm64 (use `runs-on: macos-14-arm64` if available or use matrix with archs).
  2. After both builds, fetch both dist/ManiPDF/ManiPDF executables and run `lipo -create -output ManiPDF-universal ManiPDF-x86_64 ManiPDF-arm64`.
  3. Replace the executable in the .app bundle with the universal binary.

CI notes
--------
- The macOS build job should set up a matrix for architectures or do two jobs (one for x86_64 and one for arm64) and upload artifacts. A later job can download both and run `lipo` to create the universal app before packaging the DMG.
- `hdiutil` is available on macOS runners and should be used to create compressed DMGs.

Testing
-------
- Test the DMG on both Intel and Apple Silicon Macs if possible.
- Without signing/notarization, macOS Gatekeeper will show warnings. Document these warnings in the release notes.

Pitfalls
--------
- PyInstaller and Qt plugins are often the main cause of runtime crashes. Verify the app loads and shows UI in both architectures.
- If your app uses system path lookups for Tesseract/LibreOffice, ensure the app can find them when running from a .app bundle; document how to install them.
