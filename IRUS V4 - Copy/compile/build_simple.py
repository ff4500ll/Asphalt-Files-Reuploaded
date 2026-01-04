"""
Simple IRUS V4 Build Script
Direct approach with better error handling
"""

import os
import sys
import subprocess
import shutil

def print_status(message):
    print(f"[BUILD] {message}")

def install_requirements():
    """Install required packages"""
    print_status("Installing requirements...")
    
    requirements = [
        'pyinstaller',
        'pillow',
        'opencv-python',
        'mss',
        'pyautogui', 
        'keyboard',
        'numpy'
    ]
    
    for req in requirements:
        print_status(f"Installing {req}...")
        try:
            result = subprocess.run([
                sys.executable, '-m', 'pip', 'install', req
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                print_status(f"Warning: Failed to install {req}")
                print_status(f"Error: {result.stderr}")
            else:
                print_status(f"✓ {req} installed successfully")
        except Exception as e:
            print_status(f"Error installing {req}: {e}")

def build_simple():
    """Build executable using simple PyInstaller command"""
    print_status("Building IRUS V4 executable...")
    
    if not os.path.exists("p.py"):
        print_status("ERROR: p.py not found!")
        return False
    
    # Clean previous builds
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    if os.path.exists("build"):
        shutil.rmtree("build")
    
    # Build command
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--onefile',
        '--noconsole', 
        '--name=IRUS_V4',
        '--add-data=Config.txt;.' if os.path.exists('Config.txt') else '',
        'p.py'
    ]
    
    # Remove empty string if Config.txt doesn't exist
    cmd = [c for c in cmd if c]
    
    print_status("Running PyInstaller...")
    print_status(f"Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print_status("✓ Build completed successfully!")
            
            # Check if executable exists
            exe_path = "dist/IRUS_V4.exe"
            if os.path.exists(exe_path):
                size_mb = os.path.getsize(exe_path) / 1024 / 1024
                print_status(f"✓ Executable created: {os.path.abspath(exe_path)}")
                print_status(f"✓ File size: {size_mb:.1f} MB")
                
                # Create final directory
                if not os.path.exists("final"):
                    os.makedirs("final")
                
                # Copy to final directory
                final_path = "final/IRUS_V4.exe"
                shutil.copy2(exe_path, final_path)
                print_status(f"✓ Final executable: {os.path.abspath(final_path)}")
                
                return True
            else:
                print_status("ERROR: Executable not found after build!")
                return False
                
        else:
            print_status("ERROR: PyInstaller build failed!")
            print_status(f"Error output: {result.stderr}")
            print_status(f"Standard output: {result.stdout}")
            return False
            
    except Exception as e:
        print_status(f"ERROR: Build exception: {e}")
        return False

def main():
    print_status("=" * 50)
    print_status("IRUS V4 Simple Build System")
    print_status("=" * 50)
    
    # Install requirements
    install_requirements()
    
    # Build
    if build_simple():
        print_status("=" * 50)
        print_status("🎉 BUILD SUCCESS!")
        print_status("Your executable is ready in the 'final' folder")
        print_status("File: final/IRUS_V4.exe")
        print_status("=" * 50)
        return True
    else:
        print_status("=" * 50)
        print_status("❌ BUILD FAILED!")
        print_status("Check the error messages above")
        print_status("=" * 50)
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)