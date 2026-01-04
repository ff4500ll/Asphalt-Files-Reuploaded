#!/usr/bin/env python3
"""
IRUS V4 Protection and Build Script
Creates a protected, standalone executable from p.py
"""

import os
import sys
import shutil
import subprocess
import base64
import hashlib
import random
import string
import re
from pathlib import Path

# Build configuration
BUILD_DIR = "build_protected"
DIST_DIR = "dist_final"
APP_NAME = "IRUS_V4"
ICON_PATH = None  # Add path to .ico file if you have one

def print_status(message):
    """Print colored status messages"""
    print(f"[BUILD] {message}")

def generate_random_name(length=12):
    """Generate random variable names for obfuscation"""
    return ''.join(random.choices(string.ascii_letters, k=length))

def obfuscate_strings(content):
    """Basic string obfuscation - encode sensitive strings"""
    print_status("Applying string obfuscation...")
    
    # Find and encode string literals (basic implementation)
    def encode_string(match):
        string_content = match.group(1)
        if len(string_content) > 5 and any(keyword in string_content.lower() for keyword in 
                                          ['youtube', 'asphaltcake', 'subscribe', 'terms', 'config']):
            # Encode sensitive strings
            encoded = base64.b64encode(string_content.encode()).decode()
            return f'base64.b64decode(b"{encoded}").decode()'
        return match.group(0)
    
    # Replace string literals (simple regex - not perfect but effective)
    content = re.sub(r'"([^"\\]*(\\.[^"\\]*)*)"', encode_string, content)
    content = re.sub(r"'([^'\\]*(\\.[^'\\]*)*)'", encode_string, content)
    
    return content

def add_anti_debug_protection(content):
    """Add anti-debugging and tampering protection"""
    print_status("Adding anti-debug protection...")
    
    protection_code = '''
import sys
import os
import time
import threading
import hashlib

# Anti-debugging checks
def _check_debugger():
    """Check for common debugging indicators"""
    try:
        import ctypes
        if ctypes.windll.kernel32.IsDebuggerPresent():
            sys.exit(1)
    except:
        pass
    
    # Check for common debugger processes
    try:
        import psutil
        dangerous_processes = ['ollydbg', 'x64dbg', 'windbg', 'ida', 'ida64']
        for proc in psutil.process_iter(['name']):
            if any(danger in proc.info['name'].lower() for danger in dangerous_processes):
                sys.exit(1)
    except:
        pass

def _check_vm():
    """Check for virtual machine indicators"""
    try:
        import platform
        if 'VMware' in platform.platform() or 'VirtualBox' in platform.platform():
            sys.exit(1)
    except:
        pass

def _integrity_check():
    """Basic integrity verification"""
    try:
        # Check if file has been modified
        current_file = sys.argv[0] if hasattr(sys, 'argv') else __file__
        if os.path.exists(current_file):
            with open(current_file, 'rb') as f:
                content = f.read()
            # Simple check - could be enhanced
            if len(content) < 100:  # Too small, likely tampered
                sys.exit(1)
    except:
        pass

# Run protection checks
try:
    _check_debugger()
    _check_vm()
    _integrity_check()
except:
    sys.exit(1)

# Background protection thread
def _protection_thread():
    while True:
        try:
            time.sleep(5)
            _check_debugger()
        except:
            sys.exit(1)

_protection = threading.Thread(target=_protection_thread, daemon=True)
_protection.start()

'''
    
    # Insert protection code after imports
    import_end = content.find('\n# ----------------------------------')
    if import_end != -1:
        content = content[:import_end] + protection_code + content[import_end:]
    else:
        content = protection_code + content
    
    return content

def obfuscate_code(content):
    """Apply various code obfuscation techniques"""
    print_status("Applying code obfuscation...")
    
    # Add dummy imports and variables
    dummy_code = f'''
# Obfuscation layer
import zlib
import marshal
_{generate_random_name()} = "{''.join(random.choices(string.ascii_letters + string.digits, k=100))}"
_{generate_random_name()} = lambda x: x
_{generate_random_name()} = {{i: chr(i) for i in range(256)}}

'''
    
    content = dummy_code + content
    
    # Simple variable name obfuscation for less critical variables
    # (We'll be careful not to break important functionality)
    replacements = {}
    
    # Generate obfuscated names for some common variables
    common_vars = ['temp', 'result', 'data', 'value', 'item', 'element']
    for var in common_vars:
        if f' {var} ' in content or f'{var}=' in content:
            replacements[var] = f"_{generate_random_name(8)}"
    
    for old_name, new_name in replacements.items():
        content = re.sub(rf'\b{re.escape(old_name)}\b', new_name, content)
    
    return content

def create_spec_file():
    """Create PyInstaller spec file with advanced options"""
    print_status("Creating PyInstaller spec file...")
    
    # Use absolute path to the protected file
    protected_file = os.path.abspath(f'{BUILD_DIR}/p_protected.py')
    
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    [r'{protected_file}'],
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
    hooksconfig={{}},
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
    name='{APP_NAME}',
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
    icon={'icon=' + repr(ICON_PATH) if ICON_PATH else 'None'},
)
'''
    
    spec_path = f"{BUILD_DIR}/{APP_NAME}.spec"
    with open(spec_path, "w") as f:
        f.write(spec_content)
    
    print_status(f"Spec file created at: {os.path.abspath(spec_path)}")

def install_requirements():
    """Install required packages for building"""
    print_status("Installing build requirements...")
    
    requirements = [
        'pyinstaller',
        'pillow',
        'opencv-python',
        'mss',
        'pyautogui',
        'keyboard',
        'numpy',
        'psutil'  # For anti-debug protection
    ]
    
    for req in requirements:
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', req], 
                         check=True, capture_output=True, text=True)
            print_status(f"Installed {req}")
        except subprocess.CalledProcessError as e:
            print_status(f"Warning: Could not install {req}: {e}")

def build_executable():
    """Build the final executable"""
    print_status("Building executable with PyInstaller...")
    
    try:
        # Build using spec file - use absolute paths
        spec_file = os.path.abspath(f'{BUILD_DIR}/{APP_NAME}.spec')
        
        if not os.path.exists(spec_file):
            print_status(f"ERROR: Spec file not found at {spec_file}")
            return False
            
        result = subprocess.run([
            sys.executable, '-m', 'PyInstaller',
            '--clean',
            '--noconfirm',
            spec_file
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print_status(f"PyInstaller Error: {result.stderr}")
            print_status(f"PyInstaller Output: {result.stdout}")
            return False
            
        print_status("Executable built successfully!")
        return True
        
    except Exception as e:
        print_status(f"Build failed: {e}")
        return False

def apply_upx_compression():
    """Apply UPX compression if available"""
    print_status("Checking for UPX compression...")
    
    exe_path = f"{BUILD_DIR}/dist/{APP_NAME}.exe"
    if not os.path.exists(exe_path):
        print_status("Executable not found for compression")
        return False
    
    try:
        # Try to compress with UPX
        result = subprocess.run(['upx', '--best', '--lzma', exe_path], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print_status("UPX compression applied successfully!")
            return True
        else:
            print_status("UPX not available or compression failed")
            return False
    except FileNotFoundError:
        print_status("UPX not found - skipping compression")
        return False

def main():
    """Main build process"""
    print_status("Starting IRUS V4 protection and build process...")
    
    # Clean up previous builds
    if os.path.exists(BUILD_DIR):
        shutil.rmtree(BUILD_DIR)
    if os.path.exists(DIST_DIR):
        shutil.rmtree(DIST_DIR)
    
    os.makedirs(BUILD_DIR, exist_ok=True)
    os.makedirs(DIST_DIR, exist_ok=True)
    
    # Check if source file exists
    if not os.path.exists("p.py"):
        print_status("ERROR: p.py not found!")
        return False
    
    print_status("Installing requirements...")
    install_requirements()
    
    print_status("Reading source code...")
    with open("p.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    print_status("Applying protection layers...")
    
    # Apply obfuscation techniques
    content = add_anti_debug_protection(content)
    content = obfuscate_strings(content)
    content = obfuscate_code(content)
    
    # Write protected file
    protected_file = f"{BUILD_DIR}/p_protected.py"
    with open(protected_file, "w", encoding="utf-8") as f:
        f.write(content)
    
    print_status("Creating build configuration...")
    create_spec_file()
    
    print_status("Building executable...")
    if build_executable():
        # Apply compression
        apply_upx_compression()
        
        # Look for the executable in the correct PyInstaller output location
        possible_paths = [
            f"{BUILD_DIR}/dist/{APP_NAME}.exe",
            f"dist/{APP_NAME}.exe",
            f"{APP_NAME}.exe"
        ]
        
        exe_source = None
        for path in possible_paths:
            if os.path.exists(path):
                exe_source = path
                print_status(f"Found executable at: {os.path.abspath(path)}")
                break
        
        if exe_source:
            exe_dest = f"{DIST_DIR}/{APP_NAME}.exe"
            shutil.move(exe_source, exe_dest)
            
            print_status("=" * 60)
            print_status("BUILD COMPLETED SUCCESSFULLY!")
            print_status(f"Final executable: {os.path.abspath(exe_dest)}")
            print_status(f"File size: {os.path.getsize(exe_dest) / 1024 / 1024:.1f} MB")
            print_status("=" * 60)
            print_status("Protection features applied:")
            print_status("  ✓ Anti-debugging checks")
            print_status("  ✓ Virtual machine detection")
            print_status("  ✓ String obfuscation")
            print_status("  ✓ Code obfuscation")
            print_status("  ✓ Runtime protection")
            print_status("  ✓ Single executable packaging")
            print_status("  ✓ UPX compression (if available)")
            print_status("=" * 60)
            return True
        else:
            print_status("ERROR: Executable not found after build!")
            return False
    else:
        print_status("ERROR: Build failed!")
        return False

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print_status("\nBuild process completed successfully!")
            print_status("You can now distribute the executable in the 'dist_final' folder.")
        else:
            print_status("\nBuild process failed!")
            sys.exit(1)
    except KeyboardInterrupt:
        print_status("\nBuild cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print_status(f"\nUnexpected error: {e}")
        sys.exit(1)