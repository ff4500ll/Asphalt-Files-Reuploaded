@echo off
echo ============================================================
echo Running Perfect Cast Model Training with Python 3.13 + GPU
echo ============================================================
echo.

echo Activating GPU environment...
call venv_gpu\Scripts\activate

echo.
echo Starting perfect cast model training...
python train_perfect_cast.py

pause
