import sys
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QStackedWidget, QLabel, QPushButton, QFileDialog,
    QMessageBox
)
from PySide6.QtCore import Qt

class OrganizationPanel(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<h2>Organization Tools</h2>"))
        
        self.merge_btn = QPushButton("Merge PDFs")
        self.split_btn = QPushButton("Split PDF")
        
        layout.addWidget(self.merge_btn)
        layout.addWidget(self.split_btn)
        layout.addStretch()

class SecurityPanel(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<h2>Security Tools</h2>"))
        
        self.encrypt_btn = QPushButton("Encrypt PDF")
        self.redact_btn = QPushButton("Redact Text")
        
        layout.addWidget(self.encrypt_btn)
        layout.addWidget(self.redact_btn)
        layout.addStretch()

class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("ManiPDF")
        self.setMinimumSize(1000, 700)

        # Main Layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)

        # Sidebar
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(200)
        self.sidebar.addItems(["Organization", "Security", "Modification", "Conversions", "Advanced"])
        self.sidebar.currentRowChanged.connect(self.display_panel)
        main_layout.addWidget(self.sidebar)

        # Content Area
        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack)

        # Initialize Panels
        self.org_panel = OrganizationPanel()
        self.sec_panel = SecurityPanel()
        
        self.stack.addWidget(self.org_panel)
        self.stack.addWidget(self.sec_panel)
        self.stack.addWidget(QLabel("Modification Panel (Coming Soon)"))
        self.stack.addWidget(QLabel("Conversions Panel (Coming Soon)"))
        self.stack.addWidget(QLabel("Advanced Panel (Coming Soon)"))

    def display_panel(self, index: int) -> None:
        self.stack.setCurrentIndex(index)

def main() -> None:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
