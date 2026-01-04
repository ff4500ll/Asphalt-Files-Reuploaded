@echo off
echo ============================================================
echo Running Shake Model Training with Python 3.13 + GPU
echo ============================================================
echo.

echo Activating GPU environment...
call venv_gpu\Scripts\activate

echo.
echo Starting shake model training...
python train_shake.py

pause
