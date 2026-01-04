"""
Simple test without Unicode characters for Windows compatibility
"""

def test_basic_imports():
    """Test basic imports needed for the system"""
    print("Testing basic gameplay recorder functionality...")
    
    try:
        import numpy as np
        print("[OK] NumPy imported successfully")
        
        import cv2
        print("[OK] OpenCV imported successfully")
        
        try:
            import keyboard
            print("[OK] Keyboard library imported successfully")
        except ImportError:
            print("[WARNING] Keyboard library not available")
        
        try:
            import mouse
            print("[OK] Mouse library imported successfully")
        except ImportError:
            print("[WARNING] Mouse library not available")
        
        from PIL import ImageGrab
        print("[OK] PIL ImageGrab imported successfully")
        
        import sklearn
        print("[OK] Scikit-learn imported successfully")
        
        import pickle
        print("[OK] Pickle imported successfully")
        
        import json
        print("[OK] JSON imported successfully")
        
        print("\n[SUCCESS] Core functionality test passed!")
        print("You can now record gameplay and train basic ML models.")
        return True
        
    except ImportError as e:
        print(f"[ERROR] Import error: {e}")
        return False

def test_file_creation():
    """Test if we can create data directories"""
    try:
        import os
        
        data_dir = "gameplay_data"
        sessions_dir = os.path.join(data_dir, "sessions")
        
        os.makedirs(sessions_dir, exist_ok=True)
        print(f"[OK] Created directory structure: {sessions_dir}")
        
        # Test file creation
        test_file = os.path.join(data_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("test")
        
        if os.path.exists(test_file):
            os.remove(test_file)
            print("[OK] File creation and deletion works")
            return True
        
    except Exception as e:
        print(f"[ERROR] File system error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("GAMEPLAY ML SYSTEM - COMPATIBILITY TEST")
    print("=" * 50)
    
    # Run tests
    imports_ok = test_basic_imports()
    files_ok = test_file_creation()
    
    print("\n" + "=" * 50)
    print("TEST RESULTS:")
    
    if imports_ok and files_ok:
        print("[SUCCESS] System is ready!")
        print("\nNext steps:")
        print("1. Run 'python main.py' to start")
        print("2. Choose option 1 to record gameplay")
        print("3. Use F1/F2/F3 hotkeys during recording")
    else:
        print("[FAILED] Some issues found")
        if not imports_ok:
            print("- Install missing packages with: pip install -r requirements.txt")
        if not files_ok:
            print("- Check file system permissions")