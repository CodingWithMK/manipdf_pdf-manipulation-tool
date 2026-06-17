PyInstaller .spec and PySide6 packaging tips
===========================================

This document contains example .spec snippets and guidance to ensure PySide6 and its Qt plugins are included correctly in the PyInstaller build.

Why a .spec file?
-----------------
PyInstaller's command line works for many simple apps. For PySide6 apps, you often need a .spec to explicitly collect data files, dynamic libraries, and plugins.

Example simple .spec (templates)
--------------------------------
from PyInstaller.utils.hooks import collect_all
from PyInstaller.utils.hooks import copy_metadata
import PySide6
import os

# collect all PySide6 data
py_installs = collect_all('PySide6')
datas = py_installs[0]
hiddenimports = py_installs[1]
binaries = py_installs[2]

# ensure package metadata is included
datas += copy_metadata('pyside6')

block_cipher = None

a = Analysis(
    ['run_gui.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name='ManiPDF', debug=False, bootloader_ignore_signals=False, strip=False, upx=True, console=False)
coll = COLLECT(exe, a.binaries, a.zipfiles, a.datas, strip=False, upx=True, name='ManiPDF')

Tips
----
- If your app fails to start with `Qt platform plugin not found`, ensure `PySide6/Qt/plugins/platforms` exists in the `dist` folder. You can add explicit data collection with `--add-data` or the .spec datas.
- Use PyInstaller hooks from `pyinstaller-hooks-contrib` which include many PySide6 helpers.
- On macOS, the Qt plugins need to be under `YourApp.app/Contents/MacOS/` in a structure that PySide6 expects or you must set `QT_PLUGIN_PATH` before starting.

Troubleshooting
---------------
- Use `pyinstaller --onedir --clean --log-level=DEBUG run_gui.py` to collect verbose logs while building.
- After build, run the produced executable from a terminal to see stdout/stderr; missing library messages are often visible there.
- Check for missing .dylib/.so/.dll files with `otool -L` (macOS) or `ldd` (Linux) on the main binary.
