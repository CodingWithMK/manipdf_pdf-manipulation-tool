Release Checklist
=================

Pre-release
-----------
- [ ] Confirm version number in pyproject.toml and src/manipdf/core/version.py
- [ ] Update CHANGELOG.md with release notes for the new tag
- [ ] Add LICENSE file (if missing)
- [ ] Add icons to assets/icon.ico and assets/icon.icns
- [ ] Add run_gui.py (simple wrapper that calls manipdf.gui.main.main())
- [ ] Verify README lists external dependencies and platform notes
- [ ] Run tests locally and in CI (pytest)
- [ ] Build locally on Windows and macOS (if possible) to iterate on PyInstaller .spec

CI & Build
----------
- [ ] Add `.github/workflows/release.yml` based on ci-github-actions.md
- [ ] Add `build/installer.nsi` NSIS script or generator script
- [ ] Make sure `assets/` files are checked into repo
- [ ] Confirm PyInstaller options include icon resources and data files
- [ ] For macOS universal, either ensure universal build or arrange for two-arch builds and lipo

Release
-------
- [ ] Tag the commit: `git tag -a vX.Y.Z -m "Release vX.Y.Z"`
- [ ] Push the tag: `git push origin vX.Y.Z`
- [ ] Monitor GitHub Actions to confirm all jobs succeed
- [ ] After the release is created, download artifacts and smoke-test on clean machines

Post-release
------------
- [ ] Update README with release download links
- [ ] Publish release notes to social channels if desired
- [ ] Collect user feedback and fix issues in follow-up patch releases

Notes
-----
This checklist assumes unsigned installers. If you later obtain signing certificates, add signing steps to the CI build jobs and re-run the release process with signed artifacts.
