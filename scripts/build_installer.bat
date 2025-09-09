@echo off
echo Auto Mudfish VPN Installer Builder
echo ==================================

echo Installing dependencies...
pip install -r ../requirements.txt

echo Building installer executable...
python build_installer.py

echo Build process completed!
echo.
echo Installer files created in dist/installer_package/
echo - AutoMudfishInstaller.exe (graphical installer)
echo - install_simple.bat (simple installer)
echo - README.txt (instructions)
echo.
pause
