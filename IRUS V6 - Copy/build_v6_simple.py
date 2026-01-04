#!/usr/bin/env python3
"""
Simple IRUS V6 Build Script
Creates IRUS V6.exe from p.py with all V6 improvements
"""

import subprocess
import sys
import os
from pathlib import Path
import shutil

def build_v6_simple():
    """Create IRUS V6.exe executable"""
    print("Building IRUS V6.exe...")
    
    # Clean previous builds
    if os.path.exists("dist"):
        shutil.rmtree("dist", ignore_errors=True)
    if os.path.exists("build"):
        shutil.rmtree("build", ignore_errors=True)
    
    # Simple, reliable PyInstaller command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--noconsole", 
        "--name", "IRUS_V6",
        "--clean",
        "--noconfirm",
        
        # Essential hidden imports
        "--hidden-import", "tkinter",
        "--hidden-import", "tkinter.ttk",
        "--hidden-import", "cv2",
        "--hidden-import", "numpy", 
        "--hidden-import", "PIL",
        "--hidden-import", "pyautogui",
        "--hidden-import", "keyboard",
        "--hidden-import", "pynput",
        "--hidden-import", "mss",
        
        "p.py"
    ]
    
    print("Starting PyInstaller...")
    try:
        result = subprocess.run(cmd, check=True)
        print("Build completed successfully!")
        
        exe_path = Path("dist/IRUS_V6.exe")
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"IRUS V6.exe created successfully! ({size_mb:.1f} MB)")
            print(f"Location: {exe_path.absolute()}")
            return True
        else:
            print("Build completed but executable not found!")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        return False

if __name__ == "__main__":
    build_v6_simple()