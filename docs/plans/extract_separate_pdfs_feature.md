# Plan: Extract Pages as Separate PDFs Feature

## Overview
Add a new feature to the extract functionality that allows users to extract specified pages as individual separate PDF files (one PDF per page) instead of a single combined PDF. The feature includes:
- Automatic renaming with zero-padded page numbers (e.g., `originalname_p001.pdf`, `originalname_p002.pdf`)
- User-specified folder name for output
- User-selectable save location via folder dialog
- Toggle via checkbox (GUI) / flag (CLI)

## User Requirements
- **Naming convention**: `originalname_p001.pdf` (zero-padded 3 digits with original filename prefix)
- **Output location**: Always prompt user to select folder location
- **CLI flag**: `--extract-as-separate`
- **GUI control**: Checkbox with clear description in Selective Extract tab

---

## Implementation Details

### 1. Core Logic Changes (`src/manipdf/core/organization.py`)

#### New Function: `extract_pages_as_separate_pdfs`
```python
def extract_pages_as_separate_pdfs(
    input_path: Path, 
    page_indices: list[int], 
    output_dir: Path,
    base_name: str | None = None
) -> list[Path]:
    """
    Extract specified pages as individual PDF files.
    
    Args:
        input_path: Source PDF file
        page_indices: List of 0-indexed page numbers to extract
        output_dir: Directory where individual PDFs will be saved
        base_name: Optional base name for files (defaults to input file stem)
        
    Returns:
        List of generated file paths
    """
```

**Implementation approach:**
- Open source PDF with `fitz.open(input_path)`
- For each page index in `page_indices`:
  - Create new `fitz.Document()`
  - Insert single page using `insert_pdf(doc, from_page=idx, to_page=idx)`
  - Generate filename: `{base_name}_p{page_num:03d}.pdf` (1-indexed for display)
  - Save to `output_dir`
- Return list of generated file paths

**Naming logic:**
- If `base_name` not provided, use `input_path.stem`
- Format: `{base_name}_p{page_number:03d}.pdf` where page_number = page_index + 1
- Example: `document_p001.pdf`, `document_p002.pdf`

---

### 2. CLI Changes (`src/manipdf/cli/main.py`)

#### Modify `extract` command
Add new option:
```python
extract_as_separate: bool = typer.Option(
    False, "--extract-as-separate", "-s", 
    help="Extract each page as a separate PDF file in a folder"
)
```

**Behavior when flag is set:**
1. Prompt for output directory using `QFileDialog.getExistingDirectory` (or CLI equivalent with `typer.prompt` for directory)
2. Call new core function `extract_pages_as_separate_pdfs`
3. Report number of files created and output directory

**Note:** CLI directory selection - since this is a CLI tool, we'll use `typer.prompt` for directory path input or add an `--output-dir` option.

---

### 3. GUI Changes (`src/manipdf/gui/main.py`)

#### Modify `SelectiveExtractTab` class

**UI Changes:**
1. Add checkbox below intervals input:
   ```python
   self.separate_pages_checkbox = QCheckBox(
       "Extract each page as separate PDF file\n"
       "(Creates individual files named: originalname_p001.pdf, originalname_p002.pdf, ...)"
   )
   self.separate_pages_checkbox.setToolTip(
       "When enabled, each selected page is saved as an individual PDF file "
       "inside a folder you choose. When disabled (default), all pages are "
       "combined into a single PDF."
   )
   ```
2. Add checkbox to layout between intervals input and action button

**Logic Changes:**
- In `run()` method:
  - If checkbox is checked:
    - Show folder selection dialog: `QFileDialog.getExistingDirectory(self, "Select Output Folder")`
    - If user cancels, return early
    - Call new worker function with `extract_pages_as_separate_pdfs`
    - Pass `base_name=self.file_path.stem`
  - If checkbox not checked:
    - Existing behavior (single output file via `QFileDialog.getSaveFileName`)

**Worker function call:**
```python
if self.separate_pages_checkbox.isChecked():
    output_dir = QFileDialog.getExistingDirectory(self, "Select Output Folder")
    if not output_dir: return
    self.run_task(
        self.action_btn, 
        "Extracting as separate PDFs...", 
        organization.extract_pages_as_separate_pdfs,
        self.file_path, 
        indices, 
        Path(output_dir),
        self.file_path.stem,
        gui_context={'out': output_dir, 'mode': 'extracting_separate'}
    )
else:
    # Existing single PDF extraction logic
```

**Success handling:**
- In `on_task_success`:
  - Check `mode == 'extracting_separate'`
  - Show toast with count of files created and output folder path

---

### 4. Testing (`tests/test_organization.py`)

Add new test case:
```python
def test_extract_pages_as_separate_pdfs(sample_pdf: Path, tmp_path: Path) -> None:
    output_dir = tmp_path / "separate"
    generated = extract_pages_as_separate_pdfs(sample_pdf, [0, 2], output_dir, "testdoc")
    assert len(generated) == 2
    assert all(p.exists() for p in generated)
    assert generated[0].name == "testdoc_p001.pdf"
    assert generated[1].name == "testdoc_p003.pdf"
    
    # Verify content
    with fitz.open(generated[0]) as doc:
        assert len(doc) == 1
        assert doc[0].get_text().strip() == "Page 1"
    with fitz.open(generated[1]) as doc:
        assert len(doc) == 1
        assert doc[0].get_text().strip() == "Page 3"
```

---

## File Modifications Summary

| File | Changes |
|------|---------|
| `src/manipdf/core/organization.py` | Add `extract_pages_as_separate_pdfs()` function |
| `src/manipdf/cli/main.py` | Add `--extract-as-separate` flag to `extract` command |
| `src/manipdf/gui/main.py` | Add checkbox to `SelectiveExtractTab`, modify `run()` and `on_task_success()` |
| `tests/test_organization.py` | Add test for new core function |

---

## Implementation Order

1. **Core function** - Add `extract_pages_as_separate_pdfs` to `organization.py`
2. **Unit test** - Add test case in `test_organization.py`
3. **CLI** - Add `--extract-as-separate` flag to `extract` command
4. **GUI** - Add checkbox and logic to `SelectiveExtractTab`
5. **Integration test** - Verify both CLI and GUI work correctly

---

## Edge Cases to Handle

1. **Empty page selection** - Already handled by existing validation
2. **Output directory doesn't exist** - Create with `mkdir(parents=True, exist_ok=True)`
3. **File name collisions** - Overwrite behavior (consistent with existing tools)
4. **Large number of pages** - Process sequentially to avoid memory issues
5. **User cancels folder dialog** - Graceful return without error

---

## UI/UX Considerations

- Checkbox label should be clear and descriptive
- Tooltip explains the behavior difference
- Default state: unchecked (backward compatible with current behavior)
- Success toast should indicate folder location and file count
- Progress indication during extraction (already handled by `run_task`)

---

## Future Enhancements (Out of Scope)

- Custom naming pattern configuration
- ZIP archive output option
- Parallel processing for large page counts
- Preview of generated filenames before extraction