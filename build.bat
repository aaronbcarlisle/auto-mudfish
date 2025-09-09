@echo off
echo Auto Mudfish Build Script
echo =========================

echo Installing dependencies...
pip install -r requirements.txt

echo Creating application icon...
python create_icon.py

echo Building executable...
python build_exe.py

echo Build process completed!
pause
