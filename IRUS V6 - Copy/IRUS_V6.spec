# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['p.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['tkinter', 'tkinter.ttk', 'cv2', 'numpy', 'PIL', 'pyautogui', 'keyboard', 'pynput', 'mss'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='IRUS_V6',
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
)
