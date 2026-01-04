# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['NewForge.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'cv2',
        'numpy',
        'mss',
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
        'keyboard',
        'win32gui',
        'win32con',
        'win32api',
        'tkinter',
        'tkinter.messagebox',
    ],
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
    name='NewForge',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon path here if you have an .ico file
)
