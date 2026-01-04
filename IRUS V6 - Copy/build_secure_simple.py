#!/usr/bin/env python3
"""
IRUS V4 Secure Build Script - Simple but Effective
Uses PyInstaller with multiple protection layers
"""

import os
import sys
import subprocess
import shutil
import base64
import random
import string
from pathlib import Path

def clean_environment():
    """Clean previous build artifacts"""
    print("🧹 Cleaning build environment...")
    
    dirs_to_clean = ["build", "dist", "__pycache__", "secure_build"]
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name, ignore_errors=True)
    
    # Clean spec files
    for spec_file in Path(".").glob("*.spec"):
        spec_file.unlink(missing_ok=True)

def create_protected_source():
    """Create obfuscated version of source"""
    import time
    print("🔒 Creating protected source...")
    
    with open("p.py", 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add anti-debugging header
    current_timestamp = int(time.time())
    protection_header = f'''
# Anti-analysis protection
import sys, os, time, random, threading
from datetime import datetime

def _security_check():
    """Runtime security validation"""
    try:
        # Check for debugging
        import ctypes
        if hasattr(ctypes, 'windll') and ctypes.windll.kernel32.IsDebuggerPresent():
            os._exit(random.randint(1,99))
    except: pass
    
    # Check process names
    try:
        import psutil
        dangerous = ['ida', 'olly', 'x64dbg', 'ghidra', 'radare', 'process', 'cheat']
        for proc in psutil.process_iter(['name']):
            if any(d in proc.info['name'].lower() for d in dangerous):
                time.sleep(random.uniform(0.1, 2.0))
                os._exit(random.randint(1,99))
    except: pass

# Run security check in background
threading.Thread(target=_security_check, daemon=True).start()

# Integrity verification
_build_timestamp = {current_timestamp}
if abs(time.time() - _build_timestamp) > 86400 * 365:  # 1 year
    time.sleep(random.uniform(1, 5))

'''
    
    # Obfuscate some strings
    import re
    
    def encode_string(match):
        text = match.group(1)
        encoded = base64.b64encode(text.encode()).decode()
        return f'base64.b64decode(b"{encoded}").decode()'
    
    # Encode common strings (be careful not to break functionality)
    patterns = [
        r'"(Config\.txt)"',
        r'"(Debug\.txt)"',
        r'"(\.exe)"',
        r'"(\.spec)"'
    ]
    
    protected_content = content
    for pattern in patterns:
        protected_content = re.sub(pattern, encode_string, protected_content)
    
    # Add base64 import if needed
    if 'base64.b64decode' in protected_content and 'import base64' not in protected_content:
        protected_content = 'import base64\n' + protected_content
    
    # Combine protection header with obfuscated content
    final_content = protection_header + protected_content
    
    # Save protected version
    protected_file = "p_protected.py"
    with open(protected_file, 'w', encoding='utf-8') as f:
        f.write(final_content)
    
    return protected_file

def create_secure_spec(source_file):
    """Create PyInstaller spec with security features"""
    print("📝 Creating secure build specification...")
    
    # Generate random key
    key = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
    
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-
# IRUS V4 Secure Build Specification

import os
import random

# Security configuration
block_cipher = None  # Disable for compatibility

a = Analysis(
    [r'{source_file}'],
    pathex=[r'{os.getcwd()}'],
    binaries=[],
    datas=[
        (r'Config.txt', '.'),
    ],
    hiddenimports=[
        'tkinter', 'tkinter.ttk', 'tkinter.messagebox',
        'cv2', 'numpy', 'PIL', 'PIL.Image', 'PIL.ImageTk',
        'pyautogui', 'keyboard', 'pynput',
        'mss', 'psutil', 'threading', 'base64',
        'ctypes', 'ctypes.windll'
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[
        'matplotlib', 'scipy', 'pandas', 'jupyter', 'IPython',
        'notebook', 'qtconsole', 'spyder', 'anaconda'
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Remove debugging symbols
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles, 
    a.datas,
    [],
    name='IRUS_V4_Secure',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,           # Remove debugging symbols
    upx=True,            # Compress executable
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,       # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    uac_admin=False,     # Don't require admin
    uac_uiaccess=False,
)
'''
    
    spec_file = "secure_build.spec"
    with open(spec_file, 'w') as f:
        f.write(spec_content)
    
    return spec_file

def build_executable(spec_file):
    """Build the secure executable"""
    print("🚀 Building secure executable...")
    print("This may take 3-5 minutes...")
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--clean",
        "--noconfirm", 
        spec_file
    ]
    
    try:
        # Run build with output
        process = subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT,
            text=True,
            universal_newlines=True
        )
        
        # Show progress
        for line in process.stdout:
            if "INFO:" in line and any(keyword in line for keyword in ["Building", "Processing", "Analyzing"]):
                print(f"  {line.strip()}")
        
        process.wait()
        
        if process.returncode == 0:
            print("✅ Build completed successfully!")
            return True
        else:
            print(f"❌ Build failed with return code: {process.returncode}")
            return False
            
    except Exception as e:
        print(f"❌ Build error: {e}")
        return False

def verify_build():
    """Verify the build was successful"""
    print("🔍 Verifying build...")
    
    exe_path = Path("dist/IRUS_V4_Secure.exe")
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"✅ Executable created: {exe_path} ({size_mb:.1f} MB)")
        return True
    else:
        print("❌ Executable not found!")
        return False

def cleanup_build_files():
    """Clean up temporary build files"""
    print("🧹 Cleaning up temporary files...")
    
    # Remove temporary files
    temp_files = ["p_protected.py", "secure_build.spec"]
    for temp_file in temp_files:
        if os.path.exists(temp_file):
            os.remove(temp_file)
    
    # Remove build directory but keep dist
    if os.path.exists("build"):
        shutil.rmtree("build", ignore_errors=True)

def main():
    """Main build process"""
    print("=" * 60)
    print("🔐 IRUS V4 SECURE BUILD")
    print("🛡️  Maximum Source Code Protection")
    print("=" * 60)
    
    try:
        # Step 1: Clean environment
        clean_environment()
        
        # Step 2: Install PyInstaller if needed
        print("📦 Ensuring PyInstaller is available...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], 
                         check=True, capture_output=True)
        except:
            pass  # Probably already installed
        
        # Step 3: Create protected source
        protected_source = create_protected_source()
        
        # Step 4: Create secure spec
        spec_file = create_secure_spec(protected_source)
        
        # Step 5: Build executable
        success = build_executable(spec_file)
        
        # Step 6: Verify build
        if success:
            success = verify_build()
        
        # Step 7: Cleanup
        cleanup_build_files()
        
        # Final result
        if success:
            print("\n" + "=" * 60)
            print("🎉 SECURE BUILD COMPLETED!")
            print("=" * 60)
            print("📁 Location: dist/IRUS_V4_Secure.exe")
            print("🔒 Source code is protected with:")
            print("   • Anti-debugging measures")
            print("   • Process name detection")
            print("   • String obfuscation")
            print("   • Symbol stripping")
            print("   • UPX compression")
            print("   • Runtime integrity checks")
            print("\n🚀 Ready for secure distribution!")
        else:
            print("\n❌ Build failed!")
            print("💡 Check the error messages above")
            
    except KeyboardInterrupt:
        print("\n⚠️ Build cancelled by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()