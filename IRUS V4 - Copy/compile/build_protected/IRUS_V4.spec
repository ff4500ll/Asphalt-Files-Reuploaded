# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['build_protected/p_protected.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
        'cv2',
        'numpy',
        'mss',
        'pyautogui',
        'keyboard',
        'ctypes',
        'logging',
        'threading',
        'time',
        'os',
        'sys',
        'base64',
        'hashlib',
        'webbrowser'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='IRUS_V4',
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
    cofile=None,
    icon=None,
)
