# -*- mode: python ; coding: utf-8 -*-
import sys
from PyInstaller.utils.hooks import collect_all

# Collect customtkinter and darkdetect assets
ctk_datas,  ctk_bins,  ctk_hidden  = collect_all('customtkinter')
dk_datas,   dk_bins,   dk_hidden   = collect_all('darkdetect')

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=ctk_bins + dk_bins,
    datas=ctk_datas + dk_datas,
    hiddenimports=ctk_hidden + dk_hidden,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# ── Windows / Linux: single-file .exe ──────────────────────────
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='PremiereMigrator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico' if sys.platform == 'win32' else None,
)

# ── Mac: .app bundle ───────────────────────────────────────────
if sys.platform == 'darwin':
    app = BUNDLE(
        exe,
        name='PremiereMigrator.app',
        icon='assets/icon.icns',
        bundle_identifier='com.premieremigrator.app',
        info_plist={
            'CFBundleName': 'PremiereMigrator',
            'CFBundleShortVersionString': '1.0.0',
            'CFBundleVersion': '1.0.0',
            'NSHighResolutionCapable': True,
            'LSMinimumSystemVersion': '10.15.0',
        },
    )
