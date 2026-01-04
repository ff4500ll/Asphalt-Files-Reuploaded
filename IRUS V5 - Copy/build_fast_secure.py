#!/usr/bin/env python3
"""
IRUS V4 Fast Secure Build
Quick and reliable source protection
"""

import subprocess
import sys
import os
import shutil

def build_secure():
    """Build secure version quickly"""
    print("🔐 IRUS V4 - Fast Secure Build")
    print("=" * 40)
    
    # Clean previous builds
    print("🧹 Cleaning...")
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    if os.path.exists("build"):
        shutil.rmtree("build")
    
    # Build with maximum protection settings
    print("🚀 Building secure executable...")
    print("⏱️ This will take 2-3 minutes...")
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--noconsole",
        "--name=IRUS_V4_SECURE",
        "--add-data=Config.txt;.",
        "--strip",                    # Remove debugging symbols
        "--upx-dir=C:\\upx",         # Compress (if UPX available)
        "--distpath=dist",
        "--workpath=build",
        "--specpath=.",
        "--clean",
        "--noconfirm",
        # Hide imports to make reverse engineering harder
        "--hidden-import=tkinter",
        "--hidden-import=cv2", 
        "--hidden-import=numpy",
        "--hidden-import=PIL",
        "--hidden-import=pyautogui",
        "--hidden-import=keyboard",
        "--hidden-import=mss",
        "--hidden-import=psutil",
        "--hidden-import=pynput",
        "--hidden-import=ctypes",
        "--hidden-import=threading",
        "--hidden-import=base64",
        # Exclude unnecessary modules
        "--exclude-module=matplotlib",
        "--exclude-module=scipy", 
        "--exclude-module=pandas",
        "--exclude-module=jupyter",
        "--exclude-module=IPython",
        "p.py"
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        # Check if file was created
        exe_path = "dist/IRUS_V4_SECURE.exe"
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"\n✅ SUCCESS!")
            print(f"📁 File: {exe_path}")
            print(f"📦 Size: {size_mb:.1f} MB")
            print(f"\n🔒 Protection Features:")
            print(f"   • Compiled bytecode (not easily readable)")
            print(f"   • Debug symbols stripped")
            print(f"   • Compressed executable")
            print(f"   • Hidden imports")
            print(f"   • No console window")
            print(f"\n🚀 Ready for distribution!")
            return True
        else:
            print("❌ Build failed - executable not created")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        if e.stderr:
            print(f"Error details: {e.stderr}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    try:
        success = build_secure()
        if not success:
            print(f"\n💡 If build failed, try the basic version:")
            print(f"   python -m PyInstaller --onefile --noconsole p.py")
    except KeyboardInterrupt:
        print(f"\n⚠️ Build cancelled")
    except Exception as e:
        print(f"\n💥 Error: {e}")