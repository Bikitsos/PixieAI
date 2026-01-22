# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for PixieAI

Build with: uv run pyinstaller PixieAI.spec
"""

import sys
from pathlib import Path

block_cipher = None

# Get the project root
project_root = Path(SPECPATH)

a = Analysis(
    ['main.py'],
    pathex=[str(project_root)],
    binaries=[],
    datas=[
        ('assets/icon.png', 'assets'),
        ('assets/icon.icns', 'assets'),
        ('src', 'src'),
    ],
    hiddenimports=[
        'PyQt6.QtWidgets',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'mlx',
        'mlx.core',
        'mlx_lm',
        'mlx_lm.utils',
        'mlx_lm.sample_utils',
        'ddgs',
        'src.app',
        'src.config',
        'src.gui',
        'src.gui.main_window',
        'src.gui.worker',
        'src.llm',
        'src.llm.wrapper',
        'src.search',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'IPython',
        'jupyter',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='PixieAI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # No terminal window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.icns',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='PixieAI',
)

app = BUNDLE(
    coll,
    name='PixieAI.app',
    icon='assets/icon.icns',
    bundle_identifier='com.bikitsos.pixieai',
    info_plist={
        'CFBundleName': 'PixieAI',
        'CFBundleDisplayName': 'PixieAI',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHighResolutionCapable': True,
        'LSMinimumSystemVersion': '12.0',
        'NSRequiresAquaSystemAppearance': False,
    },
)
