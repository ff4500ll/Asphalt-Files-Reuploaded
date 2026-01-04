import sys
import platform

print("=" * 60)
print("Python Version Check")
print("=" * 60)
print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")
print(f"Platform: {platform.platform()}")
print("=" * 60)

major = sys.version_info.major
minor = sys.version_info.minor

print(f"\nYou're running Python {major}.{minor}")

if minor >= 13:
    print("\n⚠ WARNING: Python 3.13+ is TOO NEW for PyTorch!")
    print("\nPyTorch currently supports: Python 3.8 - 3.12")
    print("\nSOLUTIONS:")
    print("-" * 60)
    print("\nOption 1: Install Python 3.11 or 3.12 (RECOMMENDED)")
    print("  1. Download from: https://www.python.org/downloads/")
    print("  2. Install Python 3.11.x or 3.12.x")
    print("  3. Create a virtual environment:")
    print("     py -3.11 -m venv venv")
    print("     .\\venv\\Scripts\\activate")
    print("  4. Install PyTorch with CUDA:")
    print("     pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121")
    
    print("\nOption 2: Try PyTorch nightly (may be unstable)")
    print("  pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu121")
    
    print("\nOption 3: Wait for PyTorch to support Python 3.14")
    print("  Check: https://pytorch.org/get-started/locally/")
    
elif 8 <= minor <= 12:
    print("\n✓ Your Python version is compatible with PyTorch!")
    print("\nTry these installation commands:")
    print("-" * 60)
    print("\n# For CUDA 12.1 (your GPU)")
    print("pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121")
    print("\n# Or try CUDA 11.8 if 12.1 doesn't work")
    print("pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118")
    print("\n# Or try without index-url")
    print("pip install torch torchvision torchaudio")

print("\n" + "=" * 60)
