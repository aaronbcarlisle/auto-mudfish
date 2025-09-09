@echo off
echo Auto Mudfish VPN Simple Installer Builder
echo =========================================

echo Installing PyInstaller...
pip install pyinstaller

echo Building simple installer executable...
python build_simple_installer.py

echo Build process completed!
echo.
echo Installer files created in dist/installer_package/
echo - AutoMudfishSimpleInstaller.exe (simple graphical installer)
echo - install_simple.bat (simple batch installer)
echo - README.txt (instructions)
echo.
pause
