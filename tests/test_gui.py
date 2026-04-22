import pytest
import sys
import os
from PySide6.QtWidgets import QApplication, QWidget, QTabWidget, QPushButton
from PySide6.QtCore import Qt
from manipdf.gui.main import MainWindow, SidebarButton

@pytest.fixture(scope="session")
def qapp():
    """Create the QApplication instance."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app

def test_main_window_initialization(qapp):
    """Verify window title and icon setup."""
    window = MainWindow()
    assert window.windowTitle() == "ManiPDF"
    # Verify icon is set
    assert not window.windowIcon().isNull()

def test_rounded_logo_logic(qapp):
    """Verify that the rounded pixmap generator produces a valid image."""
    window = MainWindow()
    logo_path = "docs/images/ManiPDF-logo.png"
    if os.path.exists(logo_path):
        pixmap = window.get_rounded_pixmap(logo_path, 36)
        assert not pixmap.isNull()
        assert pixmap.width() == 36
        assert pixmap.height() == 36

def test_navigation_and_state(qapp):
    """Verify navigation stack and busy state flags."""
    window = MainWindow()
    assert window.content_stack.currentIndex() == 0
    
    # Check that panels have the busy flag initialized to False
    org_panel = window.content_stack.widget(0)
    # Get the MergeTab (first tab)
    tabs = org_panel.findChild(QTabWidget)
    merge_tab = tabs.widget(0)
    assert hasattr(merge_tab, '_is_busy')
    assert merge_tab._is_busy is False

def test_sidebar_active_accent(qapp):
    """Verify red accent property toggles on sidebar buttons."""
    window = MainWindow()
    btn = window.nav_buttons[0]
    
    window.switch_page(0)
    assert btn.property("active") is True
    
    window.switch_page(1)
    assert btn.property("active") is False

def test_theme_switching_integrity(qapp):
    """Verify theme switching applies correctly without crashing."""
    window = MainWindow()
    window.apply_theme("Light")
    assert "background-color: #FAFAFA" in window.styleSheet()
    window.apply_theme("Dark")
    assert "background-color: #1E1E1E" in window.styleSheet()

def test_cursor_pointers(qapp):
    """Verify that interactive elements use the hand cursor."""
    window = MainWindow()
    # Sidebar button
    assert window.nav_buttons[0].cursor().shape() == Qt.PointingHandCursor
    
    # Theme combo
    assert window.theme_combo.cursor().shape() == Qt.PointingHandCursor
