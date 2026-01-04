#!/usr/bin/env python3
"""
Ultra Simple Build Script for IRUS V5
Minimal settings for maximum compatibility
"""

import subprocess
import sys

def ultra_simple_build():
    """Create the simplest possible executable"""
    print("🔧 IRUS V5 - ULTRA SIMPLE BUILD")
    print("=" * 50)
    
    # Ultra simple PyInstaller command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",                    # Single file
        "--name", "IRUS_V5_Simple",     # Simple name
        "p.py"                          # Source file
    ]
    
    print("🚀 Building with minimal settings...")
    try:
        subprocess.run(cmd, check=True)
        print("✅ Ultra simple build completed!")
        print("📦 Check dist/IRUS_V5_Simple.exe")
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")

if __name__ == "__main__":
    ultra_simple_build()