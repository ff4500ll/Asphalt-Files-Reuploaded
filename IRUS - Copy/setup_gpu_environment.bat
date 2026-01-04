@echo off
echo ============================================================
echo Setting up Python 3.13 GPU Environment
echo ============================================================
echo.

echo Step 1: Creating virtual environment with Python 3.13...
py -3.13 -m venv venv_gpu
echo.

echo Step 2: Activating virtual environment...
call venv_gpu\Scripts\activate
echo.

echo Step 3: Upgrading pip...
python -m pip install --upgrade pip
echo.

echo Step 4: Installing PyTorch with CUDA 12.4 support...
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
echo.

echo Step 5: Installing other required packages...
pip install ultralytics opencv-python pillow keyboard
echo.

echo Step 6: Verifying GPU installation...
python -c "import torch; print(f'\nPyTorch version: {torch.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"None\"}')"
echo.

echo ============================================================
echo Setup Complete!
echo ============================================================
echo.
echo To use this environment in the future, run:
echo   venv_gpu\Scripts\activate
echo.
echo Then you can run:
echo   python train.py
echo   python b.py
echo.
pause
