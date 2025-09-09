@echo off
echo Auto Mudfish Build Script
echo =========================

echo Installing dependencies...
pip install -r requirements.txt

echo Creating application icon...
python scripts\create_icon.py

echo Building executable...
python scripts\build_exe.py

echo Build process completed!
pause
