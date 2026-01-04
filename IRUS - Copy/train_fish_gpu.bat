@echo off
echo ============================================================
echo Running Fish Model Training with Python 3.13 + GPU
echo ============================================================
echo.

echo Activating GPU environment...
call venv_gpu\Scripts\activate

echo.
echo Starting fish model training...
python train_fish.py

pause
