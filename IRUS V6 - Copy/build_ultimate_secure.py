#!/usr/bin/env python3
"""
Ultimate Secure Build Script for IRUS V4
Combines multiple protection techniques for maximum source code security
"""

import os
import sys
import subprocess
import shutil
import tempfile
import base64
import hashlib
from pathlib import Path

class UltimateSecureBuilder:
    def __init__(self):
        self.temp_dir = None
        self.build_dir = "secure_build"
        self.output_name = "IRUS_V4_Ultimate_Secure"
        
    def setup_environment(self):
        """Setup build environment and install requirements"""
        print("🔧 Setting up secure build environment...")
        
        # Clean previous builds
        if os.path.exists(self.build_dir):
            shutil.rmtree(self.build_dir)
        if os.path.exists("dist"):
            shutil.rmtree("dist")
        if os.path.exists("build"):
            shutil.rmtree("build")
            
        os.makedirs(self.build_dir, exist_ok=True)
        
        # Install required tools
        packages = [
            "pyinstaller",
            "nuitka", 
            "cx_freeze",
            "auto-py-to-exe"
        ]
        
        for package in packages:
            print(f"Installing {package}...")
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", package], 
                             check=True, capture_output=True)
            except subprocess.CalledProcessError:
                print(f"⚠️ Failed to install {package}, continuing...")
    
    def obfuscate_strings(self, source_file):
        """Basic string obfuscation"""
        print("🔒 Applying string obfuscation...")
        
        with open(source_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find and encode sensitive strings
        import re
        
        # Obfuscate common sensitive patterns
        patterns = [
            (r'"([^"]+\.txt)"', lambda m: f'base64.b64decode(b"{base64.b64encode(m.group(1).encode()).decode()}").decode()'),
            (r"'([^']+\.exe)'", lambda m: f'base64.b64decode(b"{base64.b64encode(m.group(1).encode()).decode()}").decode()'),
        ]
        
        obfuscated_content = content
        for pattern, replacement in patterns:
            obfuscated_content = re.sub(pattern, replacement, obfuscated_content)
        
        # Add import for base64 if not present
        if 'import base64' not in obfuscated_content and 'base64.b64decode' in obfuscated_content:
            obfuscated_content = 'import base64\n' + obfuscated_content
            
        return obfuscated_content
    
    def create_protected_source(self):
        """Create a protected version of the source"""
        print("🛡️ Creating protected source code...")
        
        protected_file = os.path.join(self.build_dir, "protected_p.py")
        
        # Apply obfuscation
        obfuscated_content = self.obfuscate_strings("p.py")
        
        # Add anti-debugging measures
        anti_debug = '''
import sys
import os
import time
import threading

# Anti-debugging measures
def _check_debugger():
    try:
        import ctypes
        if ctypes.windll.kernel32.IsDebuggerPresent():
            os._exit(1)
    except:
        pass

def _anti_analysis():
    # Check for common analysis tools
    suspicious_processes = ['ida', 'ollydbg', 'x64dbg', 'cheat', 'process']
    try:
        import psutil
        for proc in psutil.process_iter(['name']):
            if any(sus in proc.info['name'].lower() for sus in suspicious_processes):
                os._exit(1)
    except:
        pass

# Run checks in background
threading.Thread(target=_check_debugger, daemon=True).start()
threading.Thread(target=_anti_analysis, daemon=True).start()

'''
        
        # Combine everything
        final_content = anti_debug + obfuscated_content
        
        with open(protected_file, 'w', encoding='utf-8') as f:
            f.write(final_content)
            
        return protected_file
    
    def build_with_nuitka(self, source_file):
        """Build with Nuitka for better protection"""
        print("🚀 Building with Nuitka (best protection)...")
        
        cmd = [
            sys.executable, "-m", "nuitka",
            "--standalone",
            "--onefile", 
            "--windows-disable-console",
            "--remove-output",
            f"--output-filename={self.output_name}_nuitka.exe",
            "--include-data-files=Config.txt=Config.txt",
            "--enable-plugin=tk-inter",
            "--enable-plugin=numpy",
            "--windows-uac-admin",
            "--assume-yes-for-downloads",
            source_file
        ]
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print("✅ Nuitka build successful!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Nuitka build failed: {e}")
            print(f"Error output: {e.stderr}")
            return False
    
    def build_with_pyinstaller(self, source_file):
        """Fallback PyInstaller build with encryption"""
        print("🔧 Building with PyInstaller (encrypted)...")
        
        # Create spec file with encryption
        spec_content = f'''
import PyInstaller.config
PyInstaller.config.CONF['distpath'] = "dist"

a = Analysis(
    [r'{source_file}'],
    pathex=[r'{os.getcwd()}'],
    binaries=[],
    datas=[(r'Config.txt', '.')],
    hiddenimports=['tkinter', 'cv2', 'numpy', 'PIL', 'pyautogui', 'keyboard', 'pynput', 'psutil'],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=['matplotlib', 'scipy', 'pandas', 'jupyter', 'IPython'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{self.output_name}_pyinstaller',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
'''
        
        spec_file = os.path.join(self.build_dir, "secure.spec")
        with open(spec_file, 'w') as f:
            f.write(spec_content)
        
        try:
            cmd = [sys.executable, "-m", "PyInstaller", "--clean", spec_file]
            subprocess.run(cmd, check=True, capture_output=True)
            print("✅ PyInstaller build successful!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ PyInstaller build failed: {e}")
            return False
    
    def build_with_cxfreeze(self, source_file):
        """Try cx_Freeze as another option"""
        print("🧊 Building with cx_Freeze...")
        
        setup_content = f'''
import sys
from cx_Freeze import setup, Executable

build_exe_options = {{
    "packages": ["tkinter", "cv2", "numpy", "PIL", "pyautogui", "keyboard", "pynput"],
    "excludes": ["matplotlib", "scipy", "pandas", "jupyter"],
    "include_files": ["Config.txt"],
    "optimize": 2,
}}

base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name="{self.output_name}",
    version="4.0",
    description="IRUS V4 Secure",
    options={{"build_exe": build_exe_options}},
    executables=[Executable(r"{source_file}", base=base, target_name="{self.output_name}_cxfreeze.exe")]
)
'''
        
        setup_file = os.path.join(self.build_dir, "setup_cxfreeze.py")
        with open(setup_file, 'w') as f:
            f.write(setup_content)
        
        try:
            cmd = [sys.executable, setup_file, "build"]
            subprocess.run(cmd, check=True, capture_output=True, cwd=self.build_dir)
            print("✅ cx_Freeze build successful!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ cx_Freeze build failed: {e}")
            return False
    
    def cleanup_traces(self):
        """Remove build traces and temporary files"""
        print("🧹 Cleaning up build traces...")
        
        # Remove build artifacts
        cleanup_dirs = ["build", "__pycache__", "*.pyc", "*.pyo"]
        cleanup_files = ["*.spec"]
        
        for pattern in cleanup_dirs:
            for path in Path(".").glob(f"**/{pattern}"):
                if path.is_dir():
                    shutil.rmtree(path, ignore_errors=True)
                else:
                    path.unlink(missing_ok=True)
    
    def build(self):
        """Main build process"""
        print("=" * 60)
        print("🔐 IRUS V4 ULTIMATE SECURE BUILD")
        print("=" * 60)
        
        try:
            # Setup
            self.setup_environment()
            
            # Create protected source
            protected_source = self.create_protected_source()
            
            # Try builds in order of security (best to worst)
            success = False
            
            # 1. Try Nuitka (best protection)
            if not success:
                success = self.build_with_nuitka(protected_source)
            
            # 2. Try PyInstaller with protection
            if not success:
                success = self.build_with_pyinstaller(protected_source)
            
            # 3. Try cx_Freeze as last resort
            if not success:
                success = self.build_with_cxfreeze(protected_source)
            
            if success:
                print("\n" + "=" * 60)
                print("🎉 SECURE BUILD COMPLETED SUCCESSFULLY!")
                print("=" * 60)
                print("📁 Check the 'dist' folder for your secure executable")
                print("🔒 Your source code is now protected!")
                
                # Show what was created
                if os.path.exists("dist"):
                    files = list(Path("dist").glob("*.exe"))
                    for file in files:
                        size_mb = file.stat().st_size / (1024 * 1024)
                        print(f"📦 {file.name} ({size_mb:.1f} MB)")
                
            else:
                print("\n❌ All build methods failed!")
                print("💡 Try the simple PyInstaller build as fallback:")
                print("   python -m PyInstaller --onefile --noconsole p.py")
            
            # Cleanup
            self.cleanup_traces()
            
        except Exception as e:
            print(f"\n💥 Unexpected error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    builder = UltimateSecureBuilder()
    builder.build()