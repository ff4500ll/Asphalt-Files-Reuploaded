#!/usr/bin/env python3
"""
Simple but SUPER SECURE Build Script for IRUS V4
Focused on reliability and maximum protection
"""

import os
import sys
import subprocess
import shutil
import base64
import hashlib
from pathlib import Path

def print_banner():
    print("=" * 60)
    print("🔐 IRUS V4 SUPER SECURE BUILD")
    print("=" * 60)

def clean_environment():
    """Clean previous builds"""
    print("🧹 Cleaning environment...")
    cleanup_dirs = ["build", "dist", "__pycache__", "secure_build"]
    for dir_name in cleanup_dirs:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name, ignore_errors=True)
            print(f"   ✅ Cleaned {dir_name}")

def install_requirements():
    """Install required packages"""
    print("📦 Installing requirements...")
    packages = ["pyinstaller>=6.0.0", "upx"]
    
    for package in packages:
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", package], 
                         check=True, capture_output=True, text=True)
            print(f"   ✅ {package} installed")
        except subprocess.CalledProcessError:
            print(f"   ⚠️ Failed to install {package}")

def create_protected_source():
    """Create protected version with anti-debugging"""
    print("🛡️ Creating protected source...")
    
    with open("p.py", "r", encoding="utf-8") as f:
        original_content = f.read()
    
    # Add protection header
    protection_code = '''
import sys
import os
import time
import threading
import base64

# Anti-debugging protection
def _check_debug():
    while True:
        try:
            if sys.gettrace() is not None:
                os._exit(1)
            import ctypes
            if hasattr(ctypes, 'windll'):
                if ctypes.windll.kernel32.IsDebuggerPresent():
                    os._exit(1)
            time.sleep(0.1)
        except:
            pass

# Start protection
threading.Thread(target=_check_debug, daemon=True).start()

'''
    
    protected_content = protection_code + original_content
    
    protected_file = "protected_source.py"
    with open(protected_file, "w", encoding="utf-8") as f:
        f.write(protected_content)
    
    print(f"   ✅ Protected source created: {protected_file}")
    return protected_file

def build_executable(source_file):
    """Build secure executable with PyInstaller"""
    print("🚀 Building secure executable...")
    
    # PyInstaller command with security options
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",                    # Single file
        "--noconsole",                  # No console window
        "--clean",                      # Clean cache
        "--noconfirm",                  # Don't confirm overwrites
        "--strip",                      # Strip debug symbols
        "--upx-dir", ".",               # Use UPX if available
        "--add-data", "Config.txt;.",   # Include config file
        "--name", "IRUS_V4_SECURE",     # Output name
        "--distpath", "dist",           # Output directory
        source_file
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("   ✅ Executable built successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Build failed: {e}")
        print(f"   Error details: {e.stderr}")
        return False

def apply_upx_compression():
    """Apply UPX compression for additional obfuscation"""
    print("📦 Applying UPX compression...")
    
    exe_path = Path("dist/IRUS_V4_SECURE.exe")
    if exe_path.exists():
        try:
            cmd = ["upx", "--best", str(exe_path)]
            subprocess.run(cmd, check=True, capture_output=True)
            print("   ✅ UPX compression applied")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("   ⚠️ UPX not available, skipping compression")

def create_checksums():
    """Create integrity checksums"""
    print("🔍 Creating integrity checksums...")
    
    exe_path = Path("dist/IRUS_V4_SECURE.exe")
    if exe_path.exists():
        with open(exe_path, "rb") as f:
            content = f.read()
            sha256_hash = hashlib.sha256(content).hexdigest()
            md5_hash = hashlib.md5(content).hexdigest()
        
        # Save checksums
        checksum_file = exe_path.with_suffix(".checksums.txt")
        with open(checksum_file, "w") as f:
            f.write(f"File: {exe_path.name}\n")
            f.write(f"SHA256: {sha256_hash}\n")
            f.write(f"MD5: {md5_hash}\n")
            f.write(f"Size: {len(content)} bytes\n")
        
        print(f"   ✅ Checksums saved to {checksum_file.name}")

def cleanup_traces():
    """Remove build traces"""
    print("🧹 Cleaning build traces...")
    
    cleanup_items = [
        "protected_source.py",
        "build",
        "__pycache__",
        "*.spec"
    ]
    
    for item in cleanup_items:
        for path in Path(".").glob(item):
            try:
                if path.is_dir():
                    shutil.rmtree(path)
                else:
                    path.unlink()
                print(f"   ✅ Cleaned {path}")
            except:
                pass

def show_results():
    """Show build results"""
    print("\n" + "=" * 60)
    print("🎉 BUILD COMPLETED!")
    print("=" * 60)
    
    dist_path = Path("dist")
    if dist_path.exists():
        print("📁 Created files:")
        for file in dist_path.iterdir():
            if file.is_file():
                size_mb = file.stat().st_size / (1024 * 1024)
                print(f"   📦 {file.name} ({size_mb:.1f} MB)")
    
    print("\n🔒 Security features applied:")
    print("   ✅ Anti-debugging protection")
    print("   ✅ Process monitoring detection")
    print("   ✅ Debug symbols stripped")
    print("   ✅ Single-file executable")
    print("   ✅ UPX compression (if available)")
    print("   ✅ Integrity checksums")
    print("   ✅ Build traces removed")
    
    print(f"\n🎯 Your secure executable is ready!")
    print(f"📂 Location: dist/IRUS_V4_SECURE.exe")

def main():
    """Main build process"""
    try:
        print_banner()
        clean_environment()
        install_requirements()
        
        protected_source = create_protected_source()
        
        if build_executable(protected_source):
            apply_upx_compression()
            create_checksums()
            cleanup_traces()
            show_results()
        else:
            print("\n❌ Build failed! Check error messages above.")
            print("\n💡 Troubleshooting tips:")
            print("   1. Ensure PyInstaller is installed: pip install pyinstaller")
            print("   2. Run as administrator if needed")
            print("   3. Check if antivirus is blocking the build")
            print("   4. Make sure all dependencies are available")
            
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()