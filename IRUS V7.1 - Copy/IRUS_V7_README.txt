IRUS V7 - Fishing Automation Executable
==========================================

BUILD INFORMATION:
- Created: October 25, 2025
- Version: V7
- Size: ~310 MB

WHAT'S INCLUDED:
✓ Complete p.py functionality
✓ Embedded fishing_model.pt (YOLO model for fish detection)
✓ Embedded shake_model.pt (YOLO model for shake detection)
✓ All required Python libraries and dependencies
✓ GUI interface (no console window)

HOW TO USE:
1. Simply run IRUS_V7.exe from the dist folder
2. No Python installation required
3. No additional files needed (models are embedded)
4. The executable is fully self-contained

LOCATION:
The executable can be found at:
dist\IRUS_V7.exe

NOTES:
- The .exe file is large because it includes:
  * PyTorch and CUDA libraries for GPU acceleration
  * Ultralytics YOLO framework
  * Computer vision libraries (OpenCV, PIL)
  * Both trained model files
  * All Python dependencies

- If you want to move the executable to another location,
  just copy IRUS_V7.exe - no other files are needed!

- The Config.txt will be created in the same directory
  as the executable when you first run it

- First run may take a few seconds to initialize

TROUBLESHOOTING:
- If Windows Defender flags it, this is normal for PyInstaller
  executables. You can safely allow it.
- Make sure you have the latest graphics drivers installed
  for GPU acceleration to work properly
