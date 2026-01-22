"""
PixieAI - Local AI Assistant

Run with: uv run main.py
"""

import multiprocessing

# Required for PyInstaller on macOS to prevent app spawning multiple instances
multiprocessing.freeze_support()

from src.app import main

if __name__ == "__main__":
    main()
