"""
PixieAI - Local AI Assistant

A macOS-native AI chat application powered by MLX and Gemma.
"""

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

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
    
    # Use native macOS style
    app.setStyle("macos")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
