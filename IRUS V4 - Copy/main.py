"""
Gameplay ML System - Main Launcher
==================================

This system can record your gameplay actions and train machine learning models to learn your patterns.

Components:
1. Gameplay Recorder - Records your inputs (keyboard, mouse, screen)
2. Gameplay Learner - Trains ML models from recorded data

Usage:
1. Run this script
2. Choose option 1 to start recording
3. Play your game while recording (F1 to start, F2 to stop)
4. Choose option 2 to train ML models on your recorded data
5. Choose option 3 to analyze your gameplay patterns

Controls during recording:
- F1: Start recording
- F2: Stop recording  
- F3: Exit program
"""

import os
import sys
import time

def print_banner():
    """Print the main banner"""
    print("🎮" + "=" * 60 + "🎮")
    print("        GAMEPLAY MACHINE LEARNING SYSTEM")
    print("          Learn and Mimic Player Behavior")
    print("🎮" + "=" * 60 + "🎮")
    print()

def print_menu():
    """Print the main menu"""
    print("📋 MAIN MENU:")
    print("1. 🔴 Record Gameplay (Capture your actions)")
    print("2. 🧠 Train ML Models (Learn from recorded data)")
    print("3. 📊 Analyze Patterns (View gameplay statistics)")
    print("4. 📦 Install Dependencies")
    print("5. ❓ Help & Information")
    print("6. 🚪 Exit")
    print()

def install_dependencies():
    """Install required Python packages"""
    print("📦 Installing required dependencies...")
    print("This may take a few minutes...")
    
    try:
        import subprocess
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Dependencies installed successfully!")
        else:
            print("❌ Error installing dependencies:")
            print(result.stderr)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Please manually run: pip install -r requirements.txt")

def check_dependencies():
    """Check if required packages are installed"""
    # Map package names to their import names
    package_map = {
        'numpy': 'numpy',
        'opencv-python': 'cv2',
        'keyboard': 'keyboard', 
        'mouse': 'mouse',
        'pillow': 'PIL',
        'scikit-learn': 'sklearn',
        'tensorflow': 'tensorflow'
    }
    
    missing_packages = []
    
    for package_name, import_name in package_map.items():
        try:
            __import__(import_name)
        except ImportError:
            # TensorFlow is optional, don't mark as missing
            if package_name != 'tensorflow':
                missing_packages.append(package_name)
            
    return missing_packages

def record_gameplay():
    """Launch the gameplay recorder"""
    print("🔴 Launching Gameplay Recorder...")
    print("Make sure your game is ready, then use the hotkeys to control recording.")
    print()
    
    try:
        from gameplay_recorder import main as recorder_main
        recorder_main()
    except ImportError as e:
        print(f"❌ Error importing recorder: {e}")
        print("Make sure all dependencies are installed (option 4)")
    except Exception as e:
        print(f"❌ Error running recorder: {e}")

def train_models():
    """Launch the ML training"""
    print("🧠 Launching ML Model Training...")
    
    try:
        from gameplay_learner import main as learner_main
        learner_main()
    except ImportError as e:
        print(f"❌ Error importing learner: {e}")
        print("Make sure all dependencies are installed (option 4)")
    except Exception as e:
        print(f"❌ Error running learner: {e}")

def analyze_patterns():
    """Analyze recorded gameplay patterns"""
    print("📊 Analyzing Gameplay Patterns...")
    
    try:
        from gameplay_learner import GameplayLearner
        
        learner = GameplayLearner()
        if learner.load_all_sessions():
            patterns = learner.analyze_gameplay_patterns()
            
            # Additional analysis
            print("\n" + "="*50)
            print("SUMMARY RECOMMENDATIONS:")
            
            total_actions = patterns['total_actions']
            if total_actions < 1000:
                print("⚠️  You have relatively few recorded actions.")
                print("   Recommendation: Record more gameplay sessions for better ML performance.")
            elif total_actions < 5000:
                print("✅ Good amount of data recorded.")
                print("   This should be sufficient for basic pattern learning.")
            else:
                print("🌟 Excellent! You have plenty of training data.")
                print("   Your ML models should perform very well.")
                
        else:
            print("❌ No recorded gameplay sessions found.")
            print("   Please record some gameplay first (option 1).")
            
    except Exception as e:
        print(f"❌ Error analyzing patterns: {e}")

def show_help():
    """Show help and information"""
    print("❓ HELP & INFORMATION")
    print("=" * 50)
    print(__doc__)
    print("\n🕒 RECOMMENDED RECORDING TIME:")
    print("For good ML performance, you should record:")
    print("• Minimum: 15-30 minutes of gameplay")
    print("• Recommended: 1-2 hours across multiple sessions") 
    print("• Optimal: 3+ hours with diverse gameplay scenarios")
    print()
    print("📝 TIPS FOR BETTER RESULTS:")
    print("• Record different game scenarios (combat, exploration, menus)")
    print("• Play consistently - avoid random clicking")
    print("• Record multiple shorter sessions rather than one long session")
    print("• Make sure the game window is visible and not minimized")
    print()
    print("🔧 TROUBLESHOOTING:")
    print("• If hotkeys don't work, run as administrator")
    print("• If mouse/keyboard not captured, check antivirus settings")
    print("• If out of memory, reduce screenshot frame rate")
    print("• If training fails, you may need more data")
    print()

def main():
    """Main function"""
    print_banner()
    
    # Check dependencies
    missing = check_dependencies()
    if missing:
        print("⚠️  Missing dependencies detected:")
        for pkg in missing:
            print(f"   - {pkg}")
        print("   Please install dependencies (option 4) before proceeding.\n")
    
    while True:
        print_menu()
        
        try:
            choice = input("👉 Enter your choice (1-6): ").strip()
            print()
            
            if choice == '1':
                if missing:
                    print("❌ Please install dependencies first (option 4)")
                else:
                    record_gameplay()
                    
            elif choice == '2':
                if missing:
                    print("❌ Please install dependencies first (option 4)")
                else:
                    train_models()
                    
            elif choice == '3':
                if missing:
                    print("❌ Please install dependencies first (option 4)")
                else:
                    analyze_patterns()
                    
            elif choice == '4':
                install_dependencies()
                # Re-check dependencies
                missing = check_dependencies()
                if not missing:
                    print("✅ All dependencies are now installed!")
                    
            elif choice == '5':
                show_help()
                
            elif choice == '6':
                print("👋 Goodbye! Happy gaming and ML training!")
                break
                
            else:
                print("❌ Invalid choice. Please enter 1-6.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Program interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            
        print("\n" + "-" * 60)
        input("Press Enter to continue...")
        print()

if __name__ == "__main__":
    main()