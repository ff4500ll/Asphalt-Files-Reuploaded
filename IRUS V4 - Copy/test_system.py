"""
Quick test script to verify the gameplay ML system is working correctly
"""

import sys
import os

def test_imports():
    """Test if all required packages can be imported"""
    print("🔍 Testing package imports...")
    
    packages = [
        ('numpy', 'np'),
        ('cv2', 'opencv-python'),
        ('keyboard', 'keyboard'),
        ('mouse', 'mouse'),
        ('PIL', 'pillow'),
        ('sklearn', 'scikit-learn'),
        ('tensorflow', 'tensorflow'),
        ('matplotlib', 'matplotlib'),
        ('pandas', 'pandas')
    ]
    
    success = True
    
    for package, name in packages:
        try:
            __import__(package)
            print(f"  ✅ {name}")
        except ImportError as e:
            print(f"  ❌ {name}: {e}")
            success = False
            
    return success

def test_file_structure():
    """Test if all required files exist"""
    print("\n📁 Testing file structure...")
    
    required_files = [
        'main.py',
        'gameplay_recorder.py', 
        'gameplay_learner.py',
        'requirements.txt',
        'README.md'
    ]
    
    success = True
    
    for file in required_files:
        if os.path.exists(file):
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} - Missing!")
            success = False
            
    return success

def test_basic_functionality():
    """Test basic functionality without recording"""
    print("\n⚙️ Testing basic functionality...")
    
    try:
        # Test recorder initialization
        from gameplay_recorder import GameplayRecorder
        recorder = GameplayRecorder(frame_rate=1)  # Low frame rate for testing
        print("  ✅ Gameplay recorder can be initialized")
        
        # Test learner initialization
        from gameplay_learner import GameplayLearner
        learner = GameplayLearner()
        print("  ✅ Gameplay learner can be initialized")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 GAMEPLAY ML SYSTEM - QUICK TEST")
    print("=" * 40)
    
    # Run tests
    imports_ok = test_imports()
    files_ok = test_file_structure()
    functionality_ok = test_basic_functionality()
    
    print("\n" + "=" * 40)
    print("📊 TEST RESULTS:")
    
    if imports_ok and files_ok and functionality_ok:
        print("🎉 ALL TESTS PASSED!")
        print("Your system is ready for gameplay recording and ML training.")
        print("\nNext steps:")
        print("1. Run 'python main.py' to start the main program")
        print("2. Choose option 1 to begin recording gameplay")
        print("3. Use F1/F2/F3 hotkeys to control recording")
    else:
        print("❌ SOME TESTS FAILED!")
        print("Please check the errors above and fix them before proceeding.")
        
        if not imports_ok:
            print("\n🔧 To fix import errors:")
            print("  Run: pip install -r requirements.txt")
            
        if not files_ok:
            print("\n🔧 To fix missing files:")
            print("  Make sure all system files are in the same directory")

if __name__ == "__main__":
    main()