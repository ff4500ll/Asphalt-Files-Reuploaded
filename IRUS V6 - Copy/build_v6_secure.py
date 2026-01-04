#!/usr/bin/env python3
"""
IRUS V6 ULTIMATE SECURE BUILD SCRIPT
Maximum source code protection with advanced obfuscation and anti-reverse engineering
"""

import os
import sys
import subprocess
import shutil
import tempfile
import base64
import hashlib
import random
import string
import time
from pathlib import Path

class IRUSV6SecureBuilder:
    def __init__(self):
        self.build_dir = "irus_v6_secure_build"
        self.output_name = "IRUS_V6_SECURE"
        self.protected_source = "protected_p_v6.py"
        
    def setup_environment(self):
        """Setup secure build environment"""
        print("=" * 70)
        print("🔒 IRUS V6 ULTIMATE SECURE BUILD")
        print("=" * 70)
        print("🛡️ Maximum source code protection")
        print("🚫 Anti-reverse engineering")
        print("🔐 Multi-layer obfuscation")
        print("⚡ All V6 performance improvements included")
        print("=" * 70)
        
        # Clean environment thoroughly
        print("\n🧹 Cleaning build environment...")
        cleanup_dirs = [self.build_dir, "dist", "build", "__pycache__"]
        for cleanup_dir in cleanup_dirs:
            if os.path.exists(cleanup_dir):
                shutil.rmtree(cleanup_dir, ignore_errors=True)
                print(f"   ✅ Cleaned {cleanup_dir}")
        
        os.makedirs(self.build_dir, exist_ok=True)
        
        # Install security tools
        print("\n📦 Installing security tools...")
        packages = [
            "pyinstaller>=6.0.0",
            "nuitka>=1.9.0"
        ]
        
        for package in packages:
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", package], 
                             check=True, capture_output=True, text=True)
                print(f"   ✅ {package} ready")
            except subprocess.CalledProcessError:
                print(f"   ⚠️ {package} installation failed, continuing...")
    
    def generate_obfuscated_name(self, prefix="", length=12):
        """Generate random obfuscated names"""
        chars = string.ascii_letters + string.digits + "_"
        return prefix + ''.join(random.choices(chars, k=length))
    
    def create_anti_debug_protection(self):
        """Create advanced anti-debugging and anti-analysis protection"""
        return '''
import sys
import os
import time
import threading
import ctypes
import hashlib
from datetime import datetime

# Advanced Anti-Analysis Protection
class _SecurityGuard:
    def __init__(self):
        self._start_time = time.time()
        self._checks_passed = 0
        
    def _check_environment(self):
        """Multi-layer environment validation"""
        try:
            # Check 1: Debugger detection
            if hasattr(ctypes, 'windll') and ctypes.windll.kernel32.IsDebuggerPresent():
                self._exit_secure()
            
            # Check 2: Execution timing analysis
            if time.time() - self._start_time > 0.1:  # Too slow = analysis
                self._exit_secure()
            
            # Check 3: Process name validation
            import psutil
            current_process = psutil.Process().name().lower()
            suspicious_names = ['ollydbg', 'x64dbg', 'ida', 'ghidra', 'cheat', 'hack']
            if any(name in current_process for name in suspicious_names):
                self._exit_secure()
                
            # Check 4: VM detection
            try:
                import wmi
                computer = wmi.WMI()
                for system in computer.Win32_ComputerSystem():
                    if 'virtual' in system.Model.lower() or 'vmware' in system.Model.lower():
                        self._exit_secure()
            except:
                pass
                
            self._checks_passed += 1
            return True
        except:
            self._exit_secure()
            
    def _exit_secure(self):
        """Secure application termination"""
        try:
            os._exit(1)
        except:
            sys.exit(1)
    
    def validate(self):
        """Main validation entry point"""
        if not self._check_environment():
            self._exit_secure()

# Initialize security guard
_guard = _SecurityGuard()
_guard.validate()

# Additional runtime protection
def _runtime_check():
    while True:
        time.sleep(1)
        _guard._check_environment()

_protection_thread = threading.Thread(target=_runtime_check, daemon=True)
_protection_thread.start()
'''

    def advanced_obfuscation(self, source_content):
        """Apply multiple layers of advanced obfuscation"""
        print("🔒 Applying advanced multi-layer obfuscation...")
        
        # Layer 1: Import obfuscation
        import_mappings = {
            'tkinter': self.generate_obfuscated_name('ui_'),
            'cv2': self.generate_obfuscated_name('vision_'), 
            'numpy': self.generate_obfuscated_name('calc_'),
            'PIL': self.generate_obfuscated_name('img_'),
            'pyautogui': self.generate_obfuscated_name('ctrl_'),
            'logging': self.generate_obfuscated_name('log_'),
            'threading': self.generate_obfuscated_name('thread_')
        }
        
        # Layer 2: String obfuscation with encryption
        def obfuscate_string(s):
            # XOR encryption with random key
            key = random.randint(1, 255)
            encrypted = ''.join([chr(ord(c) ^ key) for c in s])
            encoded = base64.b64encode(encrypted.encode('latin-1')).decode()
            return f"''.join([chr(ord(c) ^ {key}) for c in base64.b64decode(b'{encoded}').decode('latin-1')])"
        
        # Layer 3: Function name obfuscation
        function_mappings = {}
        import re
        
        # Find all function definitions
        func_pattern = r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\('
        functions = re.findall(func_pattern, source_content)
        
        for func in functions:
            if not func.startswith('_') and func not in ['__init__', '__del__']:
                function_mappings[func] = self.generate_obfuscated_name('fn_')
        
        # Apply obfuscation
        obfuscated = source_content
        
        # Replace imports
        for original, obfuscated_name in import_mappings.items():
            obfuscated = obfuscated.replace(f'import {original}', f'import {original} as {obfuscated_name}')
            obfuscated = obfuscated.replace(f'{original}.', f'{obfuscated_name}.')
        
        # Replace function names
        for original, obfuscated_name in function_mappings.items():
            obfuscated = re.sub(f'\\bdef\\s+{original}\\b', f'def {obfuscated_name}', obfuscated)
            obfuscated = re.sub(f'\\b{original}\\(', f'{obfuscated_name}(', obfuscated)
        
        # Obfuscate string literals (selective to avoid breaking functionality)
        sensitive_patterns = [
            r'"(Config\.txt)"',
            r'"(Debug\.txt)"', 
            r'"(IRUS.*?)"',
            r'"(Status:.*?)"'
        ]
        
        for pattern in sensitive_patterns:
            matches = re.findall(pattern, obfuscated)
            for match in matches:
                original_string = f'"{match}"'
                obfuscated_string = obfuscate_string(match)
                obfuscated = obfuscated.replace(original_string, obfuscated_string, 1)
        
        print("   ✅ String obfuscation applied")
        print("   ✅ Function name obfuscation applied")
        print("   ✅ Import obfuscation applied")
        
        return obfuscated
    
    def create_protected_source(self):
        """Create heavily protected source file"""
        print("\n🛡️ Creating protected source...")
        
        # Read original source
        with open("p.py", 'r', encoding='utf-8') as f:
            source_content = f.read()
        
        # Add security protection at the top
        anti_debug = self.create_anti_debug_protection()
        
        # Apply advanced obfuscation
        obfuscated_content = self.advanced_obfuscation(source_content)
        
        # Combine protection with obfuscated source
        protected_content = anti_debug + "\n" + obfuscated_content
        
        # Add additional runtime checks throughout
        protected_content = self.inject_runtime_checks(protected_content)
        
        # Write protected source
        protected_path = os.path.join(self.build_dir, self.protected_source)
        with open(protected_path, 'w', encoding='utf-8') as f:
            f.write(protected_content)
        
        print(f"   ✅ Protected source created: {self.protected_source}")
        return protected_path
    
    def inject_runtime_checks(self, content):
        """Inject runtime security checks throughout the code"""
        # Find strategic injection points
        injection_points = [
            'def __init__(self):',
            'def start_processing(self):',
            'def _process_and_control('
        ]
        
        check_code = '''
        # Runtime security validation
        if not hasattr(sys, '_getframe') or time.time() - _guard._start_time > 300:
            _guard._exit_secure()
        '''
        
        for point in injection_points:
            if point in content:
                # Inject after the function definition
                content = content.replace(
                    point,
                    point + check_code
                )
        
        return content
    
    def build_with_nuitka(self, source_path):
        """Build with Nuitka for maximum protection"""
        print("\n🚀 Building with Nuitka (Maximum Security)...")
        
        nuitka_cmd = [
            sys.executable, "-m", "nuitka",
            "--standalone",
            "--onefile",
            "--windows-disable-console",
            "--remove-output",
            "--output-filename=IRUS_V6_SECURE.exe",
            "--output-dir=dist",
            
            # Security options
            "--no-pyi-file",
            "--assume-yes-for-downloads",
            
            # Optimization
            "--enable-plugin=tk-inter",
            "--lto=yes",
            
            source_path
        ]
        
        try:
            print("   ⚡ Starting Nuitka compilation...")
            result = subprocess.run(nuitka_cmd, check=True, capture_output=True, text=True)
            print("   ✅ Nuitka build completed!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Nuitka build failed: {e}")
            return False
    
    def build_with_pyinstaller_secure(self, source_path):
        """Fallback PyInstaller build with security options"""
        print("\n🚀 Building with PyInstaller (Secure Mode)...")
        
        pyinstaller_cmd = [
            sys.executable, "-m", "PyInstaller",
            "--onefile",
            "--noconsole",
            "--clean",
            "--noconfirm",
            "--strip",
            "--optimize", "2",
            "--name", "IRUS_V6_SECURE",
            "--distpath", "dist",
            
            # Security options
            "--key", hashlib.sha256(b"IRUS_V6_SECURE_BUILD").hexdigest()[:16],
            
            # Hidden imports for V6
            "--hidden-import", "tkinter",
            "--hidden-import", "tkinter.ttk",
            "--hidden-import", "cv2", 
            "--hidden-import", "numpy",
            "--hidden-import", "PIL",
            "--hidden-import", "pyautogui",
            "--hidden-import", "keyboard",
            "--hidden-import", "pynput",
            "--hidden-import", "mss",
            "--hidden-import", "psutil",
            "--hidden-import", "threading",
            "--hidden-import", "logging",
            
            source_path
        ]
        
        try:
            print("   ⚡ Starting PyInstaller secure build...")
            result = subprocess.run(pyinstaller_cmd, check=True, capture_output=True, text=True)
            print("   ✅ PyInstaller secure build completed!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"   ❌ PyInstaller build failed: {e}")
            return False
    
    def verify_build(self):
        """Verify the secure build"""
        exe_path = Path("dist/IRUS_V6_SECURE.exe")
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"\n📊 Secure Build Analysis:")
            print(f"   🎯 File: IRUS_V6_SECURE.exe")
            print(f"   📏 Size: {size_mb:.1f} MB")
            print(f"   🔒 Protection Level: MAXIMUM")
            
            # Create security info file
            info_content = f"""IRUS V6 SECURE BUILD - MAXIMUM PROTECTION
================================================

Security Features:
🔒 Advanced multi-layer obfuscation
🛡️ Anti-debugging protection
🚫 Anti-reverse engineering measures
⚠️ VM detection and blocking
🎯 Runtime integrity checks
🔐 Encrypted string literals
📡 Continuous security monitoring

Build Information:
📦 File: IRUS_V6_SECURE.exe
📏 Size: {size_mb:.1f} MB
🕒 Build: {time.strftime('%Y-%m-%d %H:%M:%S')}
🔒 Protection: ULTIMATE SECURITY

V6 Features (Protected):
✅ Rod-specific machine learning
✅ Zero-lag logging optimization  
✅ Improved status colors
✅ Advanced parameter access
✅ Fast 1-second cooldown
✅ All performance improvements

WARNING: This executable contains advanced
protection measures. Attempting to reverse
engineer or analyze this software may cause
it to terminate automatically.

Ready for secure distribution! 🔒
"""
            
            with open("dist/IRUS_V6_SECURE_INFO.txt", "w") as f:
                f.write(info_content)
            
            return True
        return False
    
    def cleanup(self):
        """Clean up build artifacts"""
        print("\n🧹 Cleaning up build artifacts...")
        cleanup_items = [self.build_dir, "build", "__pycache__", "*.spec"]
        for item in cleanup_items:
            for path in Path(".").glob(item if "*" in item else item):
                try:
                    if path.is_dir():
                        shutil.rmtree(path)
                        print(f"   ✅ Cleaned {path}")
                except Exception:
                    pass
    
    def build(self):
        """Main build process"""
        try:
            # Setup
            self.setup_environment()
            
            # Create protected source
            protected_path = self.create_protected_source()
            
            # Try Nuitka first (maximum security)
            success = self.build_with_nuitka(protected_path)
            
            # Fallback to PyInstaller if Nuitka fails
            if not success:
                print("🔄 Falling back to PyInstaller secure build...")
                success = self.build_with_pyinstaller_secure(protected_path)
            
            if success and self.verify_build():
                print("\n" + "=" * 70)
                print("🎉 IRUS V6 SECURE BUILD COMPLETED SUCCESSFULLY!")
                print("=" * 70)
                print("🔒 Maximum source code protection applied")
                print("🛡️ Anti-reverse engineering active")
                print("⚡ All V6 performance improvements included")
                print("\n📂 Secure executable ready:")
                print("   🎯 dist/IRUS_V6_SECURE.exe")
                print("   📋 dist/IRUS_V6_SECURE_INFO.txt")
                print("\n🚨 SECURITY WARNING:")
                print("   This build contains advanced protection measures.")
                print("   Source code recovery is extremely difficult.")
                print("   Distribution-ready with maximum security! 🔐")
                print("=" * 70)
                
                # Cleanup
                self.cleanup()
                return True
            else:
                print("\n❌ Secure build failed!")
                return False
                
        except Exception as e:
            print(f"\n💥 Build error: {e}")
            return False

def main():
    """Main entry point"""
    if not os.path.exists("p.py"):
        print("❌ Source file p.py not found!")
        return False
    
    builder = IRUSV6SecureBuilder()
    return builder.build()

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)