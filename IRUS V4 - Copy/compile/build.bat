@echo off
title IRUS V4 - Simple Build Script
color 0A

echo ================================================================
echo                    IRUS V4 BUILD SYSTEM
echo                   Creating Protected Executable
echo ================================================================
echo.

echo [INFO] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

echo [INFO] Python found!
echo.

echo [INFO] Starting simple build process...
echo This may take several minutes...
echo.

REM Try the simple build first
echo [INFO] Using simple build method...
python build_simple.py

echo.
if errorlevel 1 (
    echo [WARNING] Simple build failed, trying advanced build...
    python build_protected.py
    
    if errorlevel 1 (
        echo [ERROR] Both build methods failed!
        echo.
        echo Try running manually:
        echo   python -m pip install pyinstaller pillow opencv-python mss pyautogui keyboard numpy
        echo   python -m PyInstaller --onefile --noconsole --name=IRUS_V4 p.py
        echo.
        pause
        exit /b 1
    )
)

echo.
echo [SUCCESS] Build completed successfully!
echo.
echo Your executable is ready:
if exist "final\IRUS_V4.exe" (
    echo   Location: final\IRUS_V4.exe
) else if exist "dist_final\IRUS_V4.exe" (
    echo   Location: dist_final\IRUS_V4.exe
) else if exist "dist\IRUS_V4.exe" (
    echo   Location: dist\IRUS_V4.exe
) else (
    echo   Check the folders above for IRUS_V4.exe
)
echo.
echo You can now distribute this single executable file.
echo.

pause