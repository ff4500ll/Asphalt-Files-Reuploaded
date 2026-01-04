"""
Quick test for the gameplay recorder functionality
"""

def test_recorder_basic():
    """Test basic recorder initialization"""
    try:
        from gameplay_recorder import GameplayRecorder
        
        print("Testing recorder initialization...")
        recorder = GameplayRecorder(frame_rate=1)  # Low frame rate for testing
        print("[OK] Recorder initialized successfully")
        
        # Test data directory creation
        import os
        if os.path.exists("gameplay_data"):
            print("[OK] Data directory created")
        else:
            print("[ERROR] Data directory not created")
            
        return True
        
    except Exception as e:
        print(f"[ERROR] Recorder test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing Gameplay Recorder...")
    print("=" * 40)
    
    if test_recorder_basic():
        print("\n[SUCCESS] Recorder is ready!")
        print("You can now run 'python main.py' and choose option 1 to record.")
    else:
        print("\n[FAILED] Recorder has issues.")
        print("Check the error messages above.")