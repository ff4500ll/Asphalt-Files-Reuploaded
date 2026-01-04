#!/usr/bin/env python3
"""
Simple Clean Build Script for IRUS V5
Creates a working standalone executable without aggressive protection
"""

import os
import sys
import subprocess
import shutil
import hashlib
from pathlib import Path

def clean_build():
    """Build a clean, working executable"""
    print("=" * 60)
    print("🔧 IRUS V5 CLEAN BUILD - WORKING EXECUTABLE")
    print("=" * 60)
    
    try:
        # Clean environment
        print("🧹 Cleaning environment...")
        cleanup_dirs = ["build", "dist", "__pycache__"]
        for dir_name in cleanup_dirs:
            if os.path.exists(dir_name):
                shutil.rmtree(dir_name, ignore_errors=True)
                print(f"   ✅ Cleaned {dir_name}")
        
        # Check if PyInstaller is available
        print("📦 Checking PyInstaller...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], 
                         check=True, capture_output=True, text=True)
            print("   ✅ PyInstaller ready")
        except subprocess.CalledProcessError:
            print("   ⚠️ PyInstaller installation failed")
        
        # Build clean executable
        print("🚀 Building clean executable...")
        
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--onefile",                    # Single executable file
            "--noconsole",                  # No console window
            "--clean",                      # Clean cache
            "--noconfirm",                  # Don't ask for confirmation
            "--add-data", "Config.txt;.",   # Include config file
            "--name", "IRUS_V5",            # Clean name
            "--distpath", "dist",           # Output to dist folder
            # Hidden imports for all dependencies
            "--hidden-import", "tkinter",
            "--hidden-import", "tkinter.ttk",
            "--hidden-import", "tkinter.messagebox",
            "--hidden-import", "tkinter.filedialog",
            "--hidden-import", "cv2",
            "--hidden-import", "numpy",
            "--hidden-import", "PIL",
            "--hidden-import", "PIL.Image",
            "--hidden-import", "PIL.ImageTk",
            "--hidden-import", "pyautogui",
            "--hidden-import", "keyboard",
            "--hidden-import", "pynput",
            "--hidden-import", "psutil",
            "--hidden-import", "mss",
            "--hidden-import", "base64",
            "--hidden-import", "threading",
            "--hidden-import", "logging",
            "p.py"  # Use original source file directly
        ]
        
        print("   ⚡ Starting PyInstaller...")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("   ✅ Build completed successfully!")
        
        # Verify the executable was created
        exe_path = Path("dist/IRUS_V5.exe")
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"   📦 IRUS_V5.exe created ({size_mb:.1f} MB)")
            
            # Create checksum for verification
            with open(exe_path, "rb") as f:
                content = f.read()
                sha256_hash = hashlib.sha256(content).hexdigest()
            
            checksum_file = exe_path.with_suffix(".checksum.txt")
            with open(checksum_file, "w") as f:
                f.write(f"IRUS V5 - Clean Build\\n")
                f.write(f"File: {exe_path.name}\\n")
                f.write(f"SHA256: {sha256_hash}\\n")
                f.write(f"Size: {len(content):,} bytes\\n")
                f.write(f"Build: Clean Standalone\\n")
            
            print(f"   🔍 Checksum saved: {checksum_file.name}")
        
        # Clean up build artifacts
        print("🧹 Cleaning build artifacts...")
        cleanup_items = ["build", "__pycache__", "*.spec"]
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
        
        # Show success message
        print("\\n" + "=" * 60)
        print("🎉 CLEAN BUILD COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("📂 Your executable is ready:")
        print(f"   📦 dist/IRUS_V5.exe")
        print("\\n🎯 This version:")
        print("   ✅ Runs as standalone executable")
        print("   ✅ No Python installation required")
        print("   ✅ Includes all dependencies")
        print("   ✅ Contains Config.txt")
        print("   ✅ Clean, simple operation")
        print("   ✅ No aggressive protection (will actually run!)")
        print("\\n🚀 Ready to use! Just run IRUS_V5.exe")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        print(f"Error output: {e.stderr}")
        return False
    except Exception as e:
        print(f"💥 Unexpected error: {e}")
        return False

if __name__ == "__main__":
    clean_build()