"""
PixieAI - Local AI Assistant

A macOS-native AI chat application powered by MLX and Gemma.
"""

import warnings
# Suppress harmless SWIG deprecation warnings from MLX - must be before imports
warnings.filterwarnings("ignore", category=DeprecationWarning)

import sys
import os

# Set Qt plugin path explicitly for PyQt6 on macOS
import PyQt6
qt_plugin_path = os.path.join(os.path.dirname(PyQt6.__file__), "Qt6", "plugins")
if os.path.exists(qt_plugin_path):
    os.environ["QT_PLUGIN_PATH"] = qt_plugin_path

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

from src.gui import MainWindow


def main():
    """Run the PixieAI application."""
    # Enable high DPI scaling for Retina displays
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    app = QApplication(sys.argv)
    
    # Set application metadata
    app.setApplicationName("PixieAI")
    app.setApplicationDisplayName("PixieAI")
    app.setOrganizationName("PixieAI")
    
    # Set app icon (shows in Dock)
    icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "icon.png")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    # Use native macOS style
    app.setStyle("macos")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
