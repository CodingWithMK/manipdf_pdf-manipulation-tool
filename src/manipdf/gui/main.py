import sys
import os
import io
import traceback
from pathlib import Path
from typing import Optional, Callable, List, Dict, Any

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QStackedWidget, QLabel, QPushButton, QFileDialog,
    QMessageBox, QFrame, QGraphicsDropShadowEffect, QComboBox,
    QProgressBar, QScrollArea, QListWidgetItem, QSizePolicy,
    QLineEdit, QSpinBox, QDoubleSpinBox, QCheckBox, QTabWidget,
    QFormLayout
)
from PySide6.QtCore import Qt, QSize, Signal, QObject, QThread, QRunnable, Slot, QThreadPool, QPropertyAnimation, QSequentialAnimationGroup, QPoint, QEasingCurve, QTimer, Property
from PySide6.QtGui import QIcon, QColor, QPalette, QFont, QPixmap, QCursor, QPainter, QPainterPath

from manipdf.core import organization, security, modification, conversions, advanced

# --- Styles & Constants ---
ACCENT_RED = "#E53935"
DARK_BG = "#1E1E1E"
DARK_SIDEBAR = "#252526"
LIGHT_BG = "#FAFAFA"
LIGHT_SIDEBAR = "#FFFFFF"

STYLE_SHEET = """
QMainWindow {
    background-color: %BG_COLOR%;
}

QWidget#Sidebar {
    background-color: %SIDEBAR_COLOR%;
    border-right: 1px solid %BORDER_COLOR%;
}

QPushButton#SidebarButton {
    background-color: transparent;
    color: %TEXT_COLOR%;
    border: none;
    text-align: left;
    padding: 12px 20px;
    font-size: 14px;
    font-weight: 500;
}

QPushButton#SidebarButton:hover {
    background-color: %HOVER_COLOR%;
}

QPushButton#SidebarButton[active="true"] {
    color: %ACCENT_RED%;
    font-weight: bold;
    background-color: %HOVER_COLOR%;
}

QWidget#SidebarActiveIndicator {
    background-color: %ACCENT_RED%;
}

QPushButton#PrimaryButton {
    background-color: %ACCENT_RED%;
    color: white;
    border-radius: 4px;
    padding: 10px 20px;
    font-weight: bold;
    font-size: 14px;
}

QPushButton#PrimaryButton:hover {
    background-color: #C62828;
}

QPushButton#PrimaryButton:disabled {
    background-color: #EF9A9A;
    color: #EEEEEE;
}

QFrame#DropZone {
    border: 2px dashed %BORDER_COLOR%;
    border-radius: 10px;
    background-color: %DROP_ZONE_BG%;
}

QFrame#DropZone[hover="true"] {
    border: 2px dashed %ACCENT_RED%;
    background-color: %HOVER_COLOR%;
}

QLabel {
    color: %TEXT_COLOR%;
}

QLabel#HeaderTitle {
    color: %TEXT_COLOR%;
    font-size: 24px;
    font-weight: bold;
}

QLabel#HeaderDesc {
    color: %DESC_COLOR%;
    font-size: 13px;
}

QTabWidget::pane {
    border: none;
    background-color: transparent;
}

QTabBar::tab {
    background-color: transparent;
    color: #757575;
    padding: 10px 20px;
    border-bottom: 2px solid transparent;
}

QTabBar::tab:selected {
    color: %ACCENT_RED%;
    border-bottom: 2px solid %ACCENT_RED%;
}

QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
    background-color: %INPUT_BG%;
    color: %TEXT_COLOR%;
    border: 1px solid %BORDER_COLOR%;
    padding: 8px;
    border-radius: 4px;
}

QLineEdit::placeholder {
    color: %PLACEHOLDER_COLOR%;
}

QComboBox QAbstractItemView {
    background: %INPUT_BG%;
    color: %TEXT_COLOR%;
    selection-background-color: %ACCENT_RED%;
    selection-color: white;
    border: 1px solid %BORDER_COLOR%;
}

QListWidget {
    background-color: %INPUT_BG%;
    color: %TEXT_COLOR%;
    border: 1px solid %BORDER_COLOR%;
    border-radius: 4px;
}
"""

# --- Async Worker Pattern ---

class WorkerSignals(QObject):
    finished = Signal(object)
    error = Signal(str)

class PdfWorker(QRunnable):
    def __init__(self, fn: Callable, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    @Slot()
    def run(self):
        try:
            # Only functional arguments are passed here
            result = self.fn(*self.args, **self.kwargs)
            self.signals.finished.emit(result)
        except Exception as e:
            err_msg = f"{str(e)}\n\n{traceback.format_exc()}"
            print(f"Worker Error: {err_msg}")
            self.signals.error.emit(str(e))

# --- Custom Widgets ---

class ToastNotification(QWidget):
    def __init__(self, parent_window, message, toast_type="success"):
        super().__init__(parent_window, Qt.ToolTip | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        container = QFrame()
        bg_color = "rgba(76, 175, 80, 230)" if toast_type == "success" else "rgba(244, 67, 54, 230)"
        container.setStyleSheet(f"background-color: {bg_color}; border-radius: 10px;")
        container_layout = QHBoxLayout(container)
        container_layout.setContentsMargins(20, 15, 20, 15)
        
        label = QLabel(message)
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("color: white; font-weight: bold; font-size: 14px; background: transparent;")
        container_layout.addWidget(label)
        
        layout.addWidget(container)
        self.setFixedWidth(500)
        self.adjustSize()
        
        p_geo = parent_window.geometry()
        x = p_geo.x() + (p_geo.width() - self.width()) // 2
        y = p_geo.y() + p_geo.height() - self.height() - 80
        self.move(x, y)
        
        self.opacity_anim = QPropertyAnimation(self, b"windowOpacity")
        self.opacity_anim.setDuration(400)
        self.setWindowOpacity(0)
        self.show()
        self.opacity_anim.setStartValue(0)
        self.opacity_anim.setEndValue(1)
        self.opacity_anim.start()
        QTimer.singleShot(5000, self.fade_out)

    def fade_out(self):
        self.opacity_anim.setDirection(QPropertyAnimation.Backward)
        self.opacity_anim.finished.connect(self.deleteLater)
        self.opacity_anim.start()

class SidebarButton(QPushButton):
    def __init__(self, text: str):
        super().__init__(text)
        self.setObjectName("SidebarButton")
        self.setCheckable(True)
        self.setProperty("active", False)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(50)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        self.indicator = QWidget()
        self.indicator.setObjectName("SidebarActiveIndicator")
        self.indicator.setFixedWidth(4)
        self.indicator.setVisible(False)
        layout.addWidget(self.indicator)
        layout.addSpacing(16)
        layout.addStretch()

    def set_active(self, active: bool):
        self.setProperty("active", active)
        self.indicator.setVisible(active)
        self.style().unpolish(self)
        self.style().polish(self)

class FileDropZone(QFrame):
    files_dropped = Signal(list)

    def __init__(self, multiple=True):
        super().__init__()
        self.multiple = multiple
        self.setObjectName("DropZone")
        self.setProperty("hover", False)
        self.setAcceptDrops(True)
        self.setMinimumHeight(150)
        self.setCursor(Qt.PointingHandCursor)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        
        self.label = QLabel("Drag and drop PDF files here\nor click to browse")
        self.label.setObjectName("HeaderDesc") # Reuse description style for contrast
        self.label.setStyleSheet("background: transparent;")
        layout.addWidget(self.label)

    def mousePressEvent(self, event):
        if self.multiple:
            files, _ = QFileDialog.getOpenFileNames(self, "Select PDF Files", "", "PDF Files (*.pdf);;All Files (*)")
        else:
            file, _ = QFileDialog.getOpenFileName(self, "Select PDF File", "", "PDF Files (*.pdf);;All Files (*)")
            files = [file] if file else []
        if files:
            self.files_dropped.emit([Path(f) for f in files])

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            self.setProperty("hover", True)
            self.style().unpolish(self)
            self.style().polish(self)
            event.accept()
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        self.setProperty("hover", False)
        self.style().unpolish(self)
        self.style().polish(self)

    def dragMoveEvent(self, event):
        event.accept()

    def dropEvent(self, event):
        self.setProperty("hover", False)
        self.style().unpolish(self)
        self.style().polish(self)
        files = [Path(u.toLocalFile()) for u in event.mimeData().urls()]
        if not self.multiple and len(files) > 1:
            files = files[:1]
        self.files_dropped.emit(files)

# --- Base Panels ---

class BasePanel(QWidget):
    def __init__(self, title: str, description: str):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(30, 30, 30, 30)
        self.layout.setSpacing(15)
        
        header_layout = QVBoxLayout()
        title_label = QLabel(title); title_label.setObjectName("HeaderTitle")
        desc_label = QLabel(description); desc_label.setObjectName("HeaderDesc")
        header_layout.addWidget(title_label); header_layout.addWidget(desc_label)
        self.layout.addLayout(header_layout)
        
        self.content_layout = QVBoxLayout()
        self.layout.addLayout(self.content_layout)
        self.layout.addStretch()

    def show_toast(self, message: str, toast_type="success"):
        ToastNotification(self.window(), message, toast_type)

class ToolTab(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 10, 5, 5)
        self.layout.setSpacing(10)
        self._is_busy = False

    def run_task(self, btn: QPushButton, loading_text: str, fn: Callable, *args, **kwargs):
        """Standardized way to run a background PDF task with guaranteed cleanup."""
        if self._is_busy: return
        
        # Pop GUI context before passing kwargs to the functional worker
        self._task_context = kwargs.pop('gui_context', {})
        
        self._is_busy = True
        self._active_btn = btn
        self._original_btn_text = btn.text()
        
        btn.setEnabled(False)
        btn.setText("⏳ " + loading_text)
        QApplication.setOverrideCursor(Qt.WaitCursor)
        
        worker = PdfWorker(fn, *args, **kwargs)
        worker.signals.finished.connect(self._handle_task_finished)
        worker.signals.error.connect(self._handle_task_error)
        QThreadPool.globalInstance().start(worker)

    @Slot(object)
    def _handle_task_finished(self, result):
        self._cleanup_ui()
        self.on_task_success(result)

    @Slot(str)
    def _handle_task_error(self, error_msg):
        self._cleanup_ui()
        self.on_task_error(error_msg)

    def _cleanup_ui(self):
        self._is_busy = False
        if hasattr(self, '_active_btn') and self._active_btn:
            self._active_btn.setEnabled(True)
            self._active_btn.setText(self._original_btn_text)
        QApplication.restoreOverrideCursor()

    def on_task_success(self, result):
        pass

    def on_task_error(self, error_msg):
        if hasattr(self, 'parent_panel'):
            self.parent_panel.show_toast(f"Error: {error_msg}", "error")

# --- Organization Tools ---

class MergeTab(ToolTab):
    def __init__(self, parent_panel):
        super().__init__()
        self.parent_panel = parent_panel
        self.layout.addWidget(QLabel("Combine multiple PDF files into one sequential document."))
        self.drop_zone = FileDropZone(multiple=True); self.layout.addWidget(self.drop_zone)
        self.file_list = QListWidget(); self.file_list.setDragDropMode(QListWidget.InternalMove); self.file_list.setMinimumHeight(150); self.file_list.setCursor(Qt.PointingHandCursor)
        self.layout.addWidget(QLabel("Selected Files (Drag to reorder):")); self.layout.addWidget(self.file_list)
        self.action_btn = QPushButton("Merge Files"); self.action_btn.setObjectName("PrimaryButton"); self.action_btn.setCursor(Qt.PointingHandCursor)
        self.action_btn.clicked.connect(self.run); self.layout.addWidget(self.action_btn, 0, Qt.AlignRight)
        self.drop_zone.files_dropped.connect(self.add_files)
        self.selected_files = []

    def add_files(self, paths):
        for p in paths:
            if p not in self.selected_files:
                self.selected_files.append(p); self.file_list.addItem(p.name)

    def run(self):
        if not self.selected_files or self._is_busy: return
        output, _ = QFileDialog.getSaveFileName(self, "Save Merged PDF", "merged.pdf", "PDF Files (*.pdf)")
        if not output: return
        ordered = []
        for i in range(self.file_list.count()):
            name = self.file_list.item(i).text()
            for p in self.selected_files:
                if p.name == name: ordered.append(p); break
        self.run_task(self.action_btn, "Merging...", organization.merge_pdfs, ordered, Path(output), gui_context={'out': output})

    def on_task_success(self, result):
        self.file_list.clear(); self.selected_files = []
        self.parent_panel.show_toast(f"PDFs merged successfully to:\n{self._task_context['out']}")

class SplitTab(ToolTab):
    def __init__(self, parent_panel):
        super().__init__()
        self.parent_panel = parent_panel
        self.layout.addWidget(QLabel("Split a PDF into individual pages."))
        self.drop_zone = FileDropZone(multiple=False); self.layout.addWidget(self.drop_zone)
        self.file_path = None
        self.action_btn = QPushButton("Split PDF"); self.action_btn.setObjectName("PrimaryButton"); self.action_btn.setCursor(Qt.PointingHandCursor)
        self.action_btn.clicked.connect(self.run); self.layout.addWidget(self.action_btn, 0, Qt.AlignRight)
        self.drop_zone.files_dropped.connect(self.set_file)

    def set_file(self, paths):
        if paths: self.file_path = paths[0]; self.drop_zone.label.setText(f"Selected: {self.file_path.name}")

    def run(self):
        if not self.file_path or self._is_busy: return
        output_dir = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if not output_dir: return
        self.run_task(self.action_btn, "Splitting...", organization.split_pdf, self.file_path, Path(output_dir), gui_context={'out': output_dir})

    def on_task_success(self, result):
        self.file_path = None; self.drop_zone.label.setText("Drag and drop PDF files here\nor click to browse")
        self.parent_panel.show_toast(f"PDF split into directory:\n{self._task_context['out']}")

class PageActionTab(ToolTab):
    def __init__(self, parent_panel, mode="delete"):
        super().__init__()
        self.parent_panel = parent_panel; self.mode = mode
        desc = {"delete": "Remove specific pages.", "extract": "Extract pages.", "sort": "Reorder pages.", "redact": "Black out text.", "rotate": "Rotate pages."}
        self.layout.addWidget(QLabel(desc.get(mode, "Perform operation.")))
        self.drop_zone = FileDropZone(multiple=False); self.layout.addWidget(self.drop_zone)
        self.file_path = None
        self.input_label = QLabel("Page Numbers (e.g., 1, 2, 5-8):" if mode != "redact" else "Search Text:")
        self.layout.addWidget(self.input_label)
        self.indices_input = QLineEdit(); self.layout.addWidget(self.indices_input)
        if mode == "rotate":
            self.angle_combo = QComboBox(); self.angle_combo.addItems(["90", "180", "270"]); self.layout.addWidget(self.angle_combo)
        self.action_btn = QPushButton(f"{mode.capitalize()} Pages")
        self.action_btn.setObjectName("PrimaryButton"); self.action_btn.setCursor(Qt.PointingHandCursor)
        self.action_btn.clicked.connect(self.run); self.layout.addWidget(self.action_btn, 0, Qt.AlignRight)
        self.drop_zone.files_dropped.connect(lambda p: setattr(self, 'file_path', p[0]) or self.drop_zone.label.setText(p[0].name))

    def run(self):
        if not self.file_path or self._is_busy: return
        if self.mode == "redact":
            out, _ = QFileDialog.getSaveFileName(self, "Save", "redacted.pdf", "PDF (*.pdf)")
            if not out: return
            self.run_task(self.action_btn, "Redacting...", security.redact_text, self.file_path, self.indices_input.text(), Path(out), gui_context={'out': out})
            return
        idx = self._parse_indices(self.indices_input.text())
        if idx is None and self.mode != "rotate":
            self.parent_panel.show_toast("Invalid page format.", "error"); return
        out, _ = QFileDialog.getSaveFileName(self, "Save", f"{self.mode}_result.pdf", "PDF (*.pdf)")
        if not out: return
        if self.mode == "rotate":
            worker_fn, args = organization.rotate_pages, (self.file_path, {i: int(self.angle_combo.currentText()) for i in (idx if idx else [])}, Path(out))
        else:
            fn_map = {"delete": organization.delete_pages, "extract": organization.extract_pages, "sort": organization.sort_pages}
            worker_fn, args = fn_map[self.mode], (self.file_path, idx, Path(out))
        self.run_task(self.action_btn, "Processing...", worker_fn, *args, gui_context={'out': out})

    def _parse_indices(self, text):
        indices = []
        try:
            for part in text.split(','):
                part = part.strip()
                if not part: 
                    continue
                if '-' in part:
                    s, e = map(int, part.split('-'))
                    indices.extend(range(s-1, e))
                else:
                    indices.append(int(part) - 1)
            return indices
        except: 
            return None

    def on_task_success(self, result):
        context = self._task_context.get('out', "Operation complete")
        self.file_path = None; self.indices_input.clear(); self.drop_zone.label.setText("Browse File")
        self.parent_panel.show_toast(f"Success:\n{context}")

# --- Category Panels ---

class OrganizationPanel(BasePanel):
    def __init__(self):
        super().__init__("Organization", "Manage PDF pages and structure.")
        tabs = QTabWidget(); tabs.setCursor(Qt.PointingHandCursor); tabs.tabBar().setCursor(Qt.PointingHandCursor)
        tabs.addTab(MergeTab(self), "Merge"); tabs.addTab(SplitTab(self), "Split")
        tabs.addTab(PageActionTab(self, "delete"), "Delete"); tabs.addTab(PageActionTab(self, "extract"), "Extract")
        tabs.addTab(PageActionTab(self, "sort"), "Sort"); tabs.addTab(PageActionTab(self, "rotate"), "Rotate")
        
        nup = ToolTab()
        nup.parent_panel = self
        nup.layout.addWidget(QLabel("Layout multiple pages on a single sheet."))
        dz = FileDropZone(False); nup.layout.addWidget(dz)
        grid = QHBoxLayout()
        rows = QSpinBox(); rows.setRange(1, 10); rows.setValue(2); rows.setCursor(Qt.PointingHandCursor)
        cols = QSpinBox(); cols.setRange(1, 10); cols.setValue(2); cols.setCursor(Qt.PointingHandCursor)
        grid.addWidget(QLabel("Rows:")); grid.addWidget(rows); grid.addWidget(QLabel("Cols:")); grid.addWidget(cols)
        nup.layout.addLayout(grid)
        btn = QPushButton("Create N-up"); btn.setObjectName("PrimaryButton"); btn.setCursor(Qt.PointingHandCursor); nup.layout.addWidget(btn, 0, Qt.AlignRight)
        
        nup.on_task_success = lambda r: (setattr(nup, 'path', None), dz.label.setText("Browse File"), self.show_toast(f"N-up created:\n{nup._task_context['out']}"))
        dz.files_dropped.connect(lambda p: setattr(nup, 'path', p[0]) or dz.label.setText(p[0].name))
        btn.clicked.connect(lambda: ( (out:=QFileDialog.getSaveFileName(self, "Save", "nup.pdf", "PDF (*.pdf)")[0]) and nup.run_task(btn, "Creating...", organization.nup_pdf, nup.path, rows.value(), cols.value(), Path(out), gui_context={'out': out}) ) if hasattr(nup, 'path') else None)
        tabs.addTab(nup, "N-up")

        ovl = ToolTab()
        ovl.parent_panel = self
        ovl.layout.addWidget(QLabel("Overlay (stamp) one PDF onto another."))
        dz1 = FileDropZone(False); dz1.label.setText("Main PDF"); dz2 = FileDropZone(False); dz2.label.setText("Overlay PDF")
        ovl.layout.addWidget(dz1); ovl.layout.addWidget(dz2)
        btn_ovl = QPushButton("Overlay PDFs"); btn_ovl.setObjectName("PrimaryButton"); btn_ovl.setCursor(Qt.PointingHandCursor); ovl.layout.addWidget(btn_ovl, 0, Qt.AlignRight)
        
        ovl.on_task_success = lambda r: (setattr(ovl, 'main', None), setattr(ovl, 'ovl', None), dz1.label.setText("Main PDF"), dz2.label.setText("Overlay PDF"), self.show_toast(f"Overlay complete:\n{ovl._task_context['out']}"))
        dz1.files_dropped.connect(lambda p: setattr(ovl, 'main', p[0]) or dz1.label.setText(p[0].name))
        dz2.files_dropped.connect(lambda p: setattr(ovl, 'ovl', p[0]) or dz2.label.setText(p[0].name))
        btn_ovl.clicked.connect(lambda: ( (out:=QFileDialog.getSaveFileName(self, "Save", "overlay.pdf", "PDF (*.pdf)")[0]) and ovl.run_task(btn_ovl, "Overlaying...", organization.overlay_pdf, ovl.main, ovl.ovl, Path(out), gui_context={'out': out}) ) if hasattr(ovl, 'main') and hasattr(ovl, 'ovl') else None)
        tabs.addTab(ovl, "Overlay")
        self.content_layout.addWidget(tabs)

class SecurityPanel(BasePanel):
    def __init__(self):
        super().__init__("Security", "Protect and redact sensitive information.")
        tabs = QTabWidget(); tabs.setCursor(Qt.PointingHandCursor); tabs.tabBar().setCursor(Qt.PointingHandCursor)
        
        enc = ToolTab()
        enc.parent_panel = self
        enc.layout.addWidget(QLabel("Encrypt PDF with password."))
        dz = FileDropZone(False); enc.layout.addWidget(dz)
        pw = QLineEdit(); pw.setEchoMode(QLineEdit.Password); enc.layout.addWidget(QLabel("Password:")); enc.layout.addWidget(pw)
        btn = QPushButton("Encrypt PDF"); btn.setObjectName("PrimaryButton"); btn.setCursor(Qt.PointingHandCursor); enc.layout.addWidget(btn, 0, Qt.AlignRight)
        
        enc.on_task_success = lambda r: (setattr(enc, 'path', None), pw.clear(), dz.label.setText("Browse File"), self.show_toast(f"Encrypted:\n{enc._task_context['out']}"))
        dz.files_dropped.connect(lambda p: setattr(enc, 'path', p[0]) or dz.label.setText(p[0].name))
        btn.clicked.connect(lambda: ( (out:=QFileDialog.getSaveFileName(self, "Save", "protected.pdf", "PDF (*.pdf)")[0]) and enc.run_task(btn, "Encrypting...", security.encrypt_pdf, enc.path, pw.text(), Path(out), gui_context={'out': out}) ) if hasattr(enc, 'path') and pw.text() else None)
        tabs.addTab(enc, "Encrypt")

        dec = ToolTab()
        dec.parent_panel = self
        dec.layout.addWidget(QLabel("Remove password from PDF."))
        dz_d = FileDropZone(False); dec.layout.addWidget(dz_d)
        pw_d = QLineEdit(); pw_d.setEchoMode(QLineEdit.Password); dec.layout.addWidget(QLabel("Password:")); dec.layout.addWidget(pw_d)
        btn_d = QPushButton("Decrypt PDF"); btn_d.setObjectName("PrimaryButton"); btn_d.setCursor(Qt.PointingHandCursor); dec.layout.addWidget(btn_d, 0, Qt.AlignRight)
        
        def on_dec_success(r):
            if r: (setattr(dec, 'path', None), pw_d.clear(), dz_d.label.setText("Browse File"), self.show_toast(f"Decrypted:\n{dec._task_context['out']}"))
            else: self.show_toast("Incorrect password.", "error")
        dec.on_task_success = on_dec_success
        dz_d.files_dropped.connect(lambda p: setattr(dec, 'path', p[0]) or dz_d.label.setText(p[0].name))
        btn_d.clicked.connect(lambda: ( (out:=QFileDialog.getSaveFileName(self, "Save", "unprotected.pdf", "PDF (*.pdf)")[0]) and dec.run_task(btn_d, "Decrypting...", security.decrypt_pdf, dec.path, pw_d.text(), Path(out), gui_context={'out': out}) ) if hasattr(dec, 'path') else None)
        tabs.addTab(dec, "Decrypt")

        tabs.addTab(PageActionTab(self, "redact"), "Redact")
        
        wm = ToolTab()
        wm.parent_panel = self
        wm.layout.addWidget(QLabel("Add text watermark."))
        dz_w = FileDropZone(False); wm.layout.addWidget(dz_w)
        txt = QLineEdit(); wm.layout.addWidget(QLabel("Watermark Text:")); wm.layout.addWidget(txt)
        btn_w = QPushButton("Add Watermark"); btn_w.setObjectName("PrimaryButton"); btn_w.setCursor(Qt.PointingHandCursor); wm.layout.addWidget(btn_w, 0, Qt.AlignRight)
        
        wm.on_task_success = lambda r: (setattr(wm, 'path', None), txt.clear(), dz_w.label.setText("Browse File"), self.show_toast(f"Watermark added:\n{wm._task_context['out']}"))
        dz_w.files_dropped.connect(lambda p: setattr(wm, 'path', p[0]) or dz_w.label.setText(p[0].name))
        btn_w.clicked.connect(lambda: ( (out:=QFileDialog.getSaveFileName(self, "Save", "watermarked.pdf", "PDF (*.pdf)")[0]) and wm.run_task(btn_w, "Watermarking...", security.add_watermark_text, wm.path, txt.text(), Path(out), gui_context={'out': out}) ) if hasattr(wm, 'path') else None)
        tabs.addTab(wm, "Watermark")
        self.content_layout.addWidget(tabs)

class ModificationPanel(BasePanel):
    def __init__(self):
        super().__init__("Modification", "Edit content and properties.")
        tabs = QTabWidget(); tabs.setCursor(Qt.PointingHandCursor); tabs.tabBar().setCursor(Qt.PointingHandCursor)
        
        et = ToolTab()
        et.parent_panel = self
        et.layout.addWidget(QLabel("Find and Replace Text."))
        dz = FileDropZone(False); et.layout.addWidget(dz)
        f_in = QLineEdit(); r_in = QLineEdit()
        form = QFormLayout(); form.addRow("Find:", f_in); form.addRow("Replace:", r_in); et.layout.addLayout(form)
        btn = QPushButton("Replace Text"); btn.setObjectName("PrimaryButton"); btn.setCursor(Qt.PointingHandCursor); et.layout.addWidget(btn, 0, Qt.AlignRight)
        
        et.on_task_success = lambda c: (setattr(et, 'path', None), f_in.clear(), r_in.clear(), dz.label.setText("Browse File"), self.show_toast(f"Replaced {c} instances.\nSaved to: {et._task_context['out']}"))
        dz.files_dropped.connect(lambda p: setattr(et, 'path', p[0]) or dz.label.setText(p[0].name))
        btn.clicked.connect(lambda: ( (out:=QFileDialog.getSaveFileName(self, "Save", "edited.pdf", "PDF (*.pdf)")[0]) and et.run_task(btn, "Replacing...", modification.find_replace_text, et.path, f_in.text(), r_in.text(), Path(out), gui_context={'out': out}) ) if hasattr(et, 'path') else None)
        tabs.addTab(et, "Edit Text")

        pn = ToolTab()
        pn.parent_panel = self
        pn.layout.addWidget(QLabel("Add page numbers."))
        dz_p = FileDropZone(False); pn.layout.addWidget(dz_p)
        fmt = QLineEdit(); fmt.setText("Page {page} of {total}"); pn.layout.addWidget(QLabel("Format:")); pn.layout.addWidget(fmt)
        btn_p = QPushButton("Add Page Numbers"); btn_p.setObjectName("PrimaryButton"); btn_p.setCursor(Qt.PointingHandCursor); pn.layout.addWidget(btn_p, 0, Qt.AlignRight)
        
        pn.on_task_success = lambda x: (setattr(pn, 'path', None), dz_p.label.setText("Browse File"), self.show_toast(f"Numbered:\n{pn._task_context['out']}"))
        dz_p.files_dropped.connect(lambda p: setattr(pn, 'path', p[0]) or dz_p.label.setText(p[0].name))
        btn_p.clicked.connect(lambda: ( (out:=QFileDialog.getSaveFileName(self, "Save", "numbered.pdf", "PDF (*.pdf)")[0]) and pn.run_task(btn_p, "Adding...", modification.add_page_numbers, pn.path, Path(out), text_format=fmt.text(), gui_context={'out': out}) ) if hasattr(pn, 'path') else None)
        tabs.addTab(pn, "Page Numbers")

        comp = ToolTab()
        comp.parent_panel = self
        comp.layout.addWidget(QLabel("Compress PDF size."))
        dz_c = FileDropZone(False); comp.layout.addWidget(dz_c)
        btn_c = QPushButton("Compress"); btn_c.setObjectName("PrimaryButton"); btn_c.setCursor(Qt.PointingHandCursor); comp.layout.addWidget(btn_c, 0, Qt.AlignRight)
        
        comp.on_task_success = lambda x: (setattr(comp, 'path', None), dz_c.label.setText("Browse File"), self.show_toast(f"Compressed:\n{comp._task_context['out']}"))
        dz_c.files_dropped.connect(lambda p: setattr(comp, 'path', p[0]) or dz_c.label.setText(p[0].name))
        btn_c.clicked.connect(lambda: ( (out:=QFileDialog.getSaveFileName(self, "Save", "compressed.pdf", "PDF (*.pdf)")[0]) and comp.run_task(btn_c, "Compressing...", modification.compress_pdf, comp.path, Path(out), gui_context={'out': out}) ) if hasattr(comp, 'path') else None)
        tabs.addTab(comp, "Compress")
        self.content_layout.addWidget(tabs)

class ConversionPanel(BasePanel):
    def __init__(self):
        super().__init__("Conversions", "Convert between PDF and other formats.")
        tabs = QTabWidget(); tabs.setCursor(Qt.PointingHandCursor); tabs.tabBar().setCursor(Qt.PointingHandCursor)
        
        i2p = ToolTab()
        i2p.parent_panel = self
        dz = FileDropZone(True); i2p.layout.addWidget(dz)
        btn = QPushButton("Convert to PDF"); btn.setObjectName("PrimaryButton"); btn.setCursor(Qt.PointingHandCursor); i2p.layout.addWidget(btn, 0, Qt.AlignRight)
        i2p.files = []
        i2p.on_task_success = lambda x: (setattr(i2p, 'files', []), dz.label.setText("Browse Images"), self.show_toast(f"Converted:\n{i2p._task_context['out']}"))
        dz.files_dropped.connect(lambda p: i2p.files.extend(p) or dz.label.setText(f"{len(i2p.files)} items selected"))
        btn.clicked.connect(lambda: ( (out:=QFileDialog.getSaveFileName(self, "Save", "images.pdf", "PDF (*.pdf)")[0]) and i2p.run_task(btn, "Converting...", conversions.images_to_pdf, i2p.files, Path(out), gui_context={'out': out}) ) if i2p.files else None)
        tabs.addTab(i2p, "Images to PDF")

        p2i = ToolTab()
        p2i.parent_panel = self
        dz_p = FileDropZone(False); p2i.layout.addWidget(dz_p)
        btn_p = QPushButton("Convert to Images"); btn_p.setObjectName("PrimaryButton"); btn_p.setCursor(Qt.PointingHandCursor); p2i.layout.addWidget(btn_p, 0, Qt.AlignRight)
        p2i.on_task_success = lambda x: (setattr(p2i, 'path', None), dz_p.label.setText("Browse File"), self.show_toast(f"Saved images to:\n{p2i._task_context['out']}"))
        dz_p.files_dropped.connect(lambda p: setattr(p2i, 'path', p[0]) or dz_p.label.setText(p[0].name))
        btn_p.clicked.connect(lambda: ( (out:=QFileDialog.getExistingDirectory(self, "Select Output Folder")) and p2i.run_task(btn_p, "Converting...", conversions.pdf_to_images, p2i.path, Path(out), gui_context={'out': out}) ) if hasattr(p2i, 'path') else None)
        tabs.addTab(p2i, "PDF to Images")
        self.content_layout.addWidget(tabs)

class AdvancedPanel(BasePanel):
    def __init__(self):
        super().__init__("Advanced", "OCR and complex PDF processing.")
        tabs = QTabWidget(); tabs.setCursor(Qt.PointingHandCursor); tabs.tabBar().setCursor(Qt.PointingHandCursor)
        
        ocr = ToolTab()
        ocr.parent_panel = self
        dz = FileDropZone(False); ocr.layout.addWidget(dz)
        btn = QPushButton("Run OCR"); btn.setObjectName("PrimaryButton"); btn.setCursor(Qt.PointingHandCursor); ocr.layout.addWidget(btn, 0, Qt.AlignRight)
        ocr.on_task_success = lambda x: (setattr(ocr, 'path', None), dz.label.setText("Browse File"), self.show_toast(f"OCR Complete:\n{ocr._task_context['out']}"))
        dz.files_dropped.connect(lambda p: setattr(ocr, 'path', p[0]) or dz.label.setText(p[0].name))
        btn.clicked.connect(lambda: ( (out:=QFileDialog.getSaveFileName(self, "Save", "searchable.pdf", "PDF (*.pdf)")[0]) and ocr.run_task(btn, "Running OCR...", advanced.ocr_pdf, ocr.path, Path(out), gui_context={'out': out}) ) if hasattr(ocr, 'path') else None)
        tabs.addTab(ocr, "OCR")
        
        comp = ToolTab()
        comp.parent_panel = self
        dz1 = FileDropZone(False); dz1.label.setText("First PDF"); dz2 = FileDropZone(False); dz2.label.setText("Second PDF")
        comp.layout.addWidget(dz1); comp.layout.addWidget(dz2)
        btn_c = QPushButton("Compare PDFs"); btn_c.setObjectName("PrimaryButton"); btn_c.setCursor(Qt.PointingHandCursor); comp.layout.addWidget(btn_c, 0, Qt.AlignRight)
        comp.on_task_success = lambda x: (setattr(comp, 'p1', None), setattr(comp, 'p2', None), dz1.label.setText("First PDF"), dz2.label.setText("Second PDF"), self.show_toast(f"Comparison saved:\n{comp._task_context['out']}"))
        dz1.files_dropped.connect(lambda p: setattr(comp, 'p1', p[0]) or dz1.label.setText(p[0].name))
        dz2.files_dropped.connect(lambda p: setattr(comp, 'p2', p[0]) or dz2.label.setText(p[0].name))
        btn_c.clicked.connect(lambda: ( (out:=QFileDialog.getSaveFileName(self, "Save", "compare.pdf", "PDF (*.pdf)")[0]) and comp.run_task(btn_c, "Comparing...", advanced.compare_pdfs, comp.p1, comp.p2, Path(out), gui_context={'out': out}) ) if hasattr(comp, 'p1') and hasattr(comp, 'p2') else None)
        tabs.addTab(comp, "Compare")

        bk = ToolTab()
        bk.parent_panel = self
        pgs = QSpinBox(); pgs.setValue(1); bk.layout.addWidget(QLabel("Pages:")); bk.layout.addWidget(pgs)
        btn_b = QPushButton("Create Blank"); btn_b.setObjectName("PrimaryButton"); btn_b.setCursor(Qt.PointingHandCursor); bk.layout.addWidget(btn_b, 0, Qt.AlignRight)
        bk.on_task_success = lambda x: self.show_toast(f"Created:\n{bk._task_context['out']}")
        btn_b.clicked.connect(lambda: ( (out:=QFileDialog.getSaveFileName(self, "Save", "blank.pdf", "PDF (*.pdf)")[0]) and bk.run_task(btn_b, "Creating...", advanced.create_blank_pdf, Path(out), pgs.value(), gui_context={'out': out}) ))
        tabs.addTab(bk, "Create Blank")
        self.content_layout.addWidget(tabs)

# --- Main Window ---

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ManiPDF")
        self.resize(1100, 800)
        logo_path = "docs/images/ManiPDF-logo.png"
        if os.path.exists(logo_path):
            self.setWindowIcon(QIcon(logo_path))
            QApplication.setWindowIcon(QIcon(logo_path))
        
        self.central_widget = QWidget(); self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget); self.main_layout.setContentsMargins(0, 0, 0, 0); self.main_layout.setSpacing(0)
        
        self.sidebar = QWidget(); self.sidebar.setObjectName("Sidebar"); self.sidebar.setFixedWidth(240)
        self.sidebar_layout = QVBoxLayout(self.sidebar); self.sidebar_layout.setContentsMargins(0, 20, 0, 20); self.sidebar_layout.setSpacing(5)
        
        logo_layout = QHBoxLayout(); logo_layout.setContentsMargins(20, 10, 20, 10); logo_layout.setSpacing(10)
        self.logo_label = QLabel()
        if os.path.exists(logo_path): self.logo_label.setPixmap(self.get_rounded_pixmap(logo_path, 36))
        logo_layout.addWidget(self.logo_label)
        title_label = QLabel("ManiPDF"); title_label.setStyleSheet(f"color: {ACCENT_RED}; font-size: 20px; font-weight: bold;")
        logo_layout.addWidget(title_label); logo_layout.addStretch()
        self.sidebar_layout.addLayout(logo_layout); self.sidebar_layout.addSpacing(20)
        
        self.nav_buttons = []
        categories = [("Organization", 0), ("Security", 1), ("Modification", 2), ("Conversions", 3), ("Advanced", 4)]
        for name, idx in categories:
            btn = SidebarButton(name); btn.clicked.connect(lambda checked, i=idx: self.switch_page(i))
            self.sidebar_layout.addWidget(btn); self.nav_buttons.append(btn)
        self.sidebar_layout.addStretch()
        
        theme_layout = QVBoxLayout(); theme_layout.setContentsMargins(20, 20, 20, 20)
        self.theme_combo = QComboBox(); self.theme_combo.setCursor(Qt.PointingHandCursor); self.theme_combo.addItems(["Light", "Dark"]); self.theme_combo.setCurrentText("Dark")
        self.theme_combo.currentTextChanged.connect(self.apply_theme)
        theme_layout.addWidget(QLabel("Theme:")); theme_layout.addWidget(self.theme_combo); self.sidebar_layout.addLayout(theme_layout)
        
        self.main_layout.addWidget(self.sidebar)
        self.content_stack = QStackedWidget(); self.main_layout.addWidget(self.content_stack)
        self.content_stack.addWidget(OrganizationPanel()); self.content_stack.addWidget(SecurityPanel())
        self.content_stack.addWidget(ModificationPanel()); self.content_stack.addWidget(ConversionPanel())
        self.content_stack.addWidget(AdvancedPanel())
        self.switch_page(0); self.apply_theme("Dark")
        QTimer.singleShot(100, self.refresh_cursors)

    def refresh_cursors(self):
        for btn in self.nav_buttons: btn.setCursor(Qt.PointingHandCursor)
        self.theme_combo.setCursor(Qt.PointingHandCursor)

    def get_rounded_pixmap(self, path, size):
        pixmap = QPixmap(path).scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        out_img = QPixmap(size, size); out_img.fill(Qt.transparent)
        painter = QPainter(out_img); painter.setRenderHint(QPainter.Antialiasing)
        path_obj = QPainterPath(); path_obj.addRoundedRect(0, 0, size, size, 10, 10)
        painter.setClipPath(path_obj); painter.drawPixmap(0, 0, pixmap); painter.end()
        return out_img

    def switch_page(self, index: int):
        self.content_stack.setCurrentIndex(index)
        for i, btn in enumerate(self.nav_buttons): btn.set_active(i == index)

    def apply_theme(self, theme_name: str):
        is_dark = theme_name == "Dark"
        bg = DARK_BG if is_dark else LIGHT_BG
        sidebar = DARK_SIDEBAR if is_dark else LIGHT_SIDEBAR
        text = "#FFFFFF" if is_dark else "#212121"
        desc = "#B0B0B0" if is_dark else "#616161"
        placeholder = "#616161" if is_dark else "#9E9E9E"
        hover = "#333333" if is_dark else "#F5F5F5"
        border = "#333333" if is_dark else "#E0E0E0"
        drop_bg = "#2D2D2D" if is_dark else "#F9F9F9"
        input_bg = "#252526" if is_dark else "#FFFFFF"
        
        qss = STYLE_SHEET.replace("%BG_COLOR%", bg)\
                        .replace("%SIDEBAR_COLOR%", sidebar)\
                        .replace("%TEXT_COLOR%", text)\
                        .replace("%DESC_COLOR%", desc)\
                        .replace("%PLACEHOLDER_COLOR%", placeholder)\
                        .replace("%HOVER_COLOR%", hover)\
                        .replace("%BORDER_COLOR%", border)\
                        .replace("%ACCENT_RED%", ACCENT_RED)\
                        .replace("%DROP_ZONE_BG%", drop_bg)\
                        .replace("%INPUT_BG%", input_bg)
        self.setStyleSheet(qss)

def main():
    QApplication.setApplicationName("ManiPDF")
    QApplication.setApplicationDisplayName("ManiPDF")
    app = QApplication(sys.argv)
    if sys.platform == 'darwin':
        try:
            from Foundation import NSBundle
            bundle = NSBundle.mainBundle()
            if bundle:
                info = bundle.localizedInfoDictionary() or bundle.infoDictionary()
                if info:
                    info['CFBundleName'] = "ManiPDF"
                    info['CFBundleDisplayName'] = "ManiPDF"
        except: pass
    app.setStyle("Fusion"); window = MainWindow(); window.show(); sys.exit(app.exec())

if __name__ == "__main__":
    main()
