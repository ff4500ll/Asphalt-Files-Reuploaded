#!/usr/bin/env python3
"""
IRUS V6 Optimized Build Script
Creates a high-performance executable with all V6 improvements
"""

import os
import sys
import subprocess
import shutil
import hashlib
from pathlib import Path
import time

def build_irus_v6():
    """Build optimized IRUS V6 executable"""
    print("=" * 70)
    print("🎯 IRUS V6 OPTIMIZED BUILD - PERFORMANCE EDITION")
    print("=" * 70)
    print("🚀 Building with V6 improvements:")
    print("   ✅ Rod-specific machine learning persistence")
    print("   ✅ Optimized logging system (zero lag when disabled)")
    print("   ✅ Improved status colors for white backgrounds")
    print("   ✅ Enhanced Advanced tab with all parameters")
    print("   ✅ 1-second fishing cooldown for better responsiveness")
    print("=" * 70)
    
    try:
        # Clean environment thoroughly
        print("\n🧹 Cleaning build environment...")
        cleanup_dirs = ["build", "dist", "__pycache__", "*.spec"]
        for pattern in cleanup_dirs:
            for path in Path(".").glob(pattern):
                try:
                    if path.is_dir():
                        shutil.rmtree(path, ignore_errors=True)
                        print(f"   ✅ Cleaned directory: {path}")
                    else:
                        path.unlink(missing_ok=True)
                        print(f"   ✅ Cleaned file: {path}")
                except Exception as e:
                    print(f"   ⚠️ Could not clean {path}: {e}")
        
        # Verify source file exists
        if not os.path.exists("p.py"):
            print("❌ Source file p.py not found!")
            return False
            
        # Check PyInstaller and install if needed
        print("\n📦 Setting up PyInstaller...")
        try:
            result = subprocess.run([sys.executable, "-c", "import PyInstaller"], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                print("   📥 Installing PyInstaller...")
                subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], 
                             check=True, capture_output=True)
            print("   ✅ PyInstaller ready")
        except subprocess.CalledProcessError as e:
            print(f"   ❌ PyInstaller setup failed: {e}")
            return False
        
        # Build optimized executable
        print("\n🚀 Building IRUS V6 executable...")
        
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--onefile",                           # Single executable
            "--noconsole",                         # No console window (GUI app)
            "--clean",                             # Clean PyInstaller cache
            "--noconfirm",                         # No confirmation prompts
            "--optimize", "2",                     # Maximum Python optimization
            "--name", "IRUS_V6",                   # V6 executable name
            "--distpath", "dist",                  # Output directory
            
            # Include essential data files
            "--add-data", "Config.txt;." if os.path.exists("Config.txt") else "",
            
            # Critical hidden imports for IRUS functionality
            "--hidden-import", "tkinter",
            "--hidden-import", "tkinter.ttk", 
            "--hidden-import", "tkinter.messagebox",
            "--hidden-import", "tkinter.filedialog",
            "--hidden-import", "tkinter.simpledialog",
            
            # Computer Vision and Image Processing
            "--hidden-import", "cv2",
            "--hidden-import", "numpy",
            "--hidden-import", "PIL",
            "--hidden-import", "PIL.Image",
            "--hidden-import", "PIL.ImageTk",
            "--hidden-import", "PIL.ImageDraw",
            "--hidden-import", "PIL.ImageFont",
            
            # Input Control
            "--hidden-import", "pyautogui",
            "--hidden-import", "keyboard", 
            "--hidden-import", "pynput",
            "--hidden-import", "pynput.keyboard",
            "--hidden-import", "pynput.mouse",
            
            # Screen Capture
            "--hidden-import", "mss",
            
            # System and Utilities
            "--hidden-import", "psutil",
            "--hidden-import", "threading",
            "--hidden-import", "logging",
            "--hidden-import", "json",
            "--hidden-import", "base64",
            "--hidden-import", "hashlib",
            "--hidden-import", "time",
            "--hidden-import", "datetime",
            "--hidden-import", "asyncio",
            "--hidden-import", "urllib.request",
            "--hidden-import", "urllib.parse",
            
            # Windows-specific
            "--hidden-import", "ctypes",
            "--hidden-import", "ctypes.wintypes",
            
            # Performance optimizations
            "--strip",                             # Strip debug symbols
            
            "p.py"  # Source file
        ]
        
        # Remove empty add-data arguments
        cmd = [arg for arg in cmd if arg.strip()]
        
        print("   ⚡ Starting PyInstaller build process...")
        print("   📋 Build configuration:")
        print(f"      🎯 Target: IRUS V6.exe")
        print(f"      📦 Mode: Single file executable")
        print(f"      🖥️ Interface: GUI (no console)")
        print(f"      ⚡ Optimization: Maximum")
        
        # Execute build with progress indication
        start_time = time.time()
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        build_time = time.time() - start_time
        
        print(f"   ✅ Build completed in {build_time:.1f} seconds!")
        
        # Verify and analyze the executable
        exe_path = Path("dist/IRUS_V6.exe")
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"\n📊 Build Analysis:")
            print(f"   📦 File: IRUS_V6.exe")
            print(f"   📏 Size: {size_mb:.1f} MB")
            print(f"   ⏱️ Build Time: {build_time:.1f} seconds")
            
            # Create comprehensive checksum and info file
            with open(exe_path, "rb") as f:
                content = f.read()
                sha256_hash = hashlib.sha256(content).hexdigest()
                md5_hash = hashlib.md5(content).hexdigest()
            
            info_file = exe_path.with_suffix(".info.txt")
            with open(info_file, "w") as f:
                f.write("IRUS V6 - Optimized Performance Build\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"Build Information:\n")
                f.write(f"  Version: IRUS V6\n")
                f.write(f"  File: {exe_path.name}\n")
                f.write(f"  Size: {len(content):,} bytes ({size_mb:.1f} MB)\n")
                f.write(f"  Build Time: {build_time:.1f} seconds\n")
                f.write(f"  Build Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(f"Checksums:\n")
                f.write(f"  SHA256: {sha256_hash}\n")
                f.write(f"  MD5: {md5_hash}\n\n")
                f.write(f"V6 Features:\n")
                f.write(f"  ✅ Rod-specific ML learning persistence\n")
                f.write(f"  ✅ Zero-lag logging system\n") 
                f.write(f"  ✅ Improved status colors\n")
                f.write(f"  ✅ Advanced parameter access\n")
                f.write(f"  ✅ 1-second fishing cooldown\n")
                f.write(f"  ✅ Enhanced performance optimizations\n\n")
                f.write(f"Requirements:\n")
                f.write(f"  - Windows 10/11 (64-bit recommended)\n")
                f.write(f"  - No Python installation required\n")
                f.write(f"  - All dependencies included\n\n")
                f.write(f"Usage:\n")
                f.write(f"  Simply run IRUS_V6.exe - no installation needed!\n")
            
            print(f"   📋 Build info saved: {info_file.name}")
            
            # Final cleanup
            print(f"\n🧹 Final cleanup...")
            cleanup_items = ["build", "__pycache__"]
            for item in cleanup_items:
                for path in Path(".").glob(item):
                    try:
                        if path.is_dir():
                            shutil.rmtree(path)
                            print(f"   ✅ Cleaned: {path}")
                    except Exception as e:
                        pass
            
            # Success message
            print("\n" + "=" * 70)
            print("🎉 IRUS V6 BUILD COMPLETED SUCCESSFULLY!")
            print("=" * 70)
            print(f"📂 Your optimized executable is ready:")
            print(f"   🎯 dist/IRUS_V6.exe ({size_mb:.1f} MB)")
            print(f"   📋 dist/IRUS_V6.info.txt (build details)")
            print("\n🚀 IRUS V6 Features:")
            print("   ✅ Rod-specific machine learning persistence")
            print("   ✅ Zero-lag logging when Output Debug disabled")
            print("   ✅ Readable status colors on white backgrounds") 
            print("   ✅ Advanced tab with all hidden parameters")
            print("   ✅ Fast 1-second fishing cooldown")
            print("   ✅ Maximum performance optimizations")
            print("\n🎮 Ready to use!")
            print("   Just run IRUS_V6.exe - no Python installation required!")
            print("=" * 70)
            
            return True
            
        else:
            print("❌ Executable not found after build!")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Build failed!")
        print(f"Error: {e}")
        if e.stderr:
            print(f"Details: {e.stderr}")
        print("\n🔧 Troubleshooting tips:")
        print("   1. Make sure p.py exists in current directory")
        print("   2. Check if all required packages are installed")
        print("   3. Try running: pip install pyinstaller")
        print("   4. Make sure no antivirus is blocking the build")
        return False
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = build_irus_v6()
    if not success:
        sys.exit(1)