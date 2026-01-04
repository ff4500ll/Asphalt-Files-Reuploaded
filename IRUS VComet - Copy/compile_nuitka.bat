@echo off
echo ========================================
echo  IRUS COMET - Nuitka Compilation
echo ========================================
echo.

REM Check if Nuitka is installed
python -m nuitka --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Nuitka not found! Installing...
    pip install nuitka
    echo.
)

echo Starting compilation with Nuitka...
echo This may take 5-15 minutes depending on your PC.
echo.

REM Check if icon exists
if exist icon.ico (
    echo Found icon.ico - using custom icon
    set ICON_FLAG=--windows-icon-from-ico=icon.ico
) else (
    echo No icon.ico found - using default icon
    set ICON_FLAG=
)

REM Compile with Nuitka
python -m nuitka ^
    --standalone ^
    --onefile ^
    --windows-console-mode=disable ^
    --enable-plugin=tk-inter ^
    %ICON_FLAG% ^
    --company-name="AsphaltCake" ^
    --product-name="IRUS COMET" ^
    --file-version=1.0.0.0 ^
    --product-version=1.0.0.0 ^
    --file-description="IRUS COMET Fishing Bot" ^
    --copyright="(c) 2025 AsphaltCake" ^
    --output-filename="IRUS_COMET.exe" ^
    --output-dir=dist ^
    --follow-imports ^
    --assume-yes-for-downloads ^
    p.py

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo  Compilation SUCCESS!
    echo ========================================
    echo.
    echo Your executable is ready:
    echo   dist\IRUS_COMET.exe
    echo.
    echo You can distribute this single .exe file!
    echo ========================================
) else (
    echo.
    echo ========================================
    echo  Compilation FAILED!
    echo ========================================
    echo Check the error messages above.
)
    p.py

echo.
if %errorlevel% equ 0 (
    echo ========================================
    echo  Compilation SUCCESS!
    echo ========================================
    echo.
    echo Executable location: dist\IRUS_COMET.exe
    echo.
) else (
    echo ========================================
    echo  Compilation FAILED!
    echo ========================================
    echo Check the error messages above.
    echo.
)

pause
