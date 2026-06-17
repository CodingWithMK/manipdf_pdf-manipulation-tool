# Master Implementation Plan: Phase 5 - GUI Adapter Layer Integration

## 1. Vision & UI/UX Philosophy
The goal for Phase 5 is to transition ManiPDF from a powerful CLI-only tool into an accessible, modern desktop application. The GUI must prioritize an intuitive user experience (UX) and an aesthetic user interface (UI) that appeals to both general users and power users.

### 1.1 Core Design Language
*   **Aesthetic**: Modern, Sleek, Minimalist, Flat Design.
*   **Accent Color**: **Crimson Red (`#D32F2F` or `#E53935`)** to represent action, power, and the traditional color associated with PDF documents. The red accent will highlight active states, primary buttons, and key interactions.
*   **Themes**: The application will support three themes, selectable via a dropdown menu in the top-right corner:
    *   **System (Default)**: Automatically syncs with the OS settings.
    *   **Light Theme**: Clean, crisp backgrounds (`#FAFAFA` and `#FFFFFF`) with dark typography.
    *   **Dark Theme**: Professional, eye-strain-reducing backgrounds (`#1E1E1E` and `#252526`) with light typography.
*   **Layout Structure**: A robust, two-pane layout consisting of a fixed Navigation Sidebar on the left and a dynamic Content Area on the right.

---

## 2. Layout Wireframes & UI Structure

### 2.1 Main Window Layout

```text
+---------------------------------------------------------------------------------+
|  [ManiPDF Logo]                                        [Theme: System|v] [-][O][X]|
+-------------------------+-------------------------------------------------------+
|  NAVIGATION             |  [  CONTENT AREA (QStackedWidget)                  ]  |
|                         |                                                       |
|  [ ] Organization       |                                                       |
|  [ ] Security           |                                                       |
|  [x] Modification (Red) |                                                       |
|  [ ] Conversions        |                                                       |
|  [ ] Advanced           |                                                       |
|                         |                                                       |
|                         |                                                       |
|                         |                                                       |
|                         |                                                       |
|                         |                                                       |
|  [ Settings (Icon) ]    |                                                       |
+-------------------------+-------------------------------------------------------+
```

### 2.2 Active State Behavior (Sidebar)
When a category is selected in the sidebar:
1.  The button background subtly changes to indicate focus.
2.  A **solid red vertical indicator bar** appears on the left edge of the active button.
3.  The icon and text of the active button tint to the **red accent color**.

### 2.3 Standard Tool Panel Layout (e.g., Merge PDFs)

Each tool panel within the Content Area will follow a standardized layout to ensure consistency.

```text
+---------------------------------------------------------------------------------+
|  < Back to Organization                                                         |
|                                                                                 |
|  Merge PDFs                                                                     |
|  Combine multiple PDF files into a single document.                             |
|  -----------------------------------------------------------------------------  |
|                                                                                 |
|  +---------------------------------------------------------------------------+  |
|  |                                                                           |  |
|  |                           [ + Add Files... ]                              |  |
|  |                  or drag and drop PDF files here                          |  |
|  |                                                                           |  |
|  +---------------------------------------------------------------------------+  |
|                                                                                 |
|  Selected Files (Drag to reorder):                                              |
|  [::] 1. document_A.pdf                                                [ x ]    |
|  [::] 2. document_B.pdf                                                [ x ]    |
|                                                                                 |
|  [x] Open file after merging                                                    |
|                                                                                 |
|                                                     [   Merge Files (Red)  ]    |
+---------------------------------------------------------------------------------+
```

---

## 3. Implementation Strategy (Step-by-Step)

### Step 1: Scaffolding and Theming Engine (PySide6)
*   Setup the main application loop, `QMainWindow`, and `QSS` (Qt Style Sheets) engine.
*   Implement `ThemeManager` for "System", "Light", and "Dark" transitions.
*   Define global red accent variables (`#E53935`).

### Step 2: Main Layout and Navigation
*   Implement the `QHBoxLayout` separating the Sidebar and Content Area.
*   Create a custom `Sidebar` widget with the red vertical indicator logic for the active category.
*   Initialize `QStackedWidget` for panel management.

### Step 3: Reusable UI Components
*   `FileDropZone`: Drag-and-drop area with file selection button.
*   `FileListWidget`: List of files with drag-to-reorder and deletion.
*   `ToastNotification`: Sleek overlays for success/error feedback.
*   `LoadingOverlay`: To block interaction during background tasks.

### Step 4: Category & Tool Panels
*   Create specific views for Organization, Security, Modification, Conversions, and Advanced.
*   Each tool opens its own parameter editor/file selector within the main view.

### Step 5: Asynchronous Core Wiring
*   Use `QThread` and `QRunnable` (Worker pattern) for all `src/manipdf/core/` calls.
*   Ensure the UI remains responsive during long operations (OCR, Compression).
*   Strict adherence to **100% local processing**.

---

## 4. Architectural Guidelines for GUI
*   **Threading**: No core calls on the Main Thread. Use signals/slots for state updates.
*   **Validation**: Real-time validation of file paths and parameters before enabling the "Action" button.
*   **Error Handling**: Styled red-accented error messages instead of system dialogs where possible.
