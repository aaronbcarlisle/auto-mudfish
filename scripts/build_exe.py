#!/usr/bin/env python3
"""
Build script for creating executable from Auto Mudfish GUI.

This script uses PyInstaller to create a standalone executable that includes
all dependencies and can be distributed without requiring Python installation.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def clean_build_dirs():
    """Clean previous build directories."""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"Cleaning {dir_name}...")
            shutil.rmtree(dir_name)
    
    # Clean .spec files
    for spec_file in Path('.').glob('*.spec'):
        print(f"Removing {spec_file}...")
        spec_file.unlink()


def build_executable():
    """Build the executable using PyInstaller."""
    print("Building Auto Mudfish executable...")
    
    # PyInstaller command
    cmd = [
        'pyinstaller',
        '--onefile',  # Create a single executable file
        '--windowed',  # No console window (GUI only)
        '--name=AutoMudfish',
        '--icon=assets/icon.ico',  # Application icon (if available)
        '--add-data=src/auto_mudfish;auto_mudfish',  # Include the package
        '--hidden-import=PyQt6.QtCore',
        '--hidden-import=PyQt6.QtGui',
        '--hidden-import=PyQt6.QtWidgets',
        '--hidden-import=selenium',
        '--hidden-import=requests',
        '--hidden-import=beautifulsoup4',
        '--hidden-import=psutil',
        '--hidden-import=win32crypt',
        '--hidden-import=win32api',
        '--hidden-import=get_chrome_driver',
        '--collect-all=PyQt6',
        '--collect-all=selenium',
        '--collect-all=requests',
        '--collect-all=beautifulsoup4',
        '--collect-all=psutil',
        '--collect-all=pywin32',
        '--collect-all=get_chrome_driver',
        '--exclude-module=tkinter',  # Exclude tkinter to reduce size
        '--exclude-module=matplotlib',  # Exclude matplotlib to reduce size
        '--exclude-module=numpy',  # Exclude numpy to reduce size
        '--exclude-module=pandas',  # Exclude pandas to reduce size
        'src/gui/gui.py'
    ]
    
    # Remove icon parameter if icon file doesn't exist
    if not os.path.exists('assets/icon.ico'):
        cmd = [arg for arg in cmd if not arg.startswith('--icon')]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("Build completed successfully!")
        print(f"Executable location: {os.path.join('dist', 'AutoMudfish.exe')}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Build failed with error: {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        return False


def create_installer_script():
    """Create a simple installer script."""
    installer_content = '''@echo off
echo Auto Mudfish VPN Installer
echo ==========================

echo Installing Auto Mudfish VPN...

REM Create application directory
if not exist "%PROGRAMFILES%\\Auto Mudfish" mkdir "%PROGRAMFILES%\\Auto Mudfish"

REM Copy executable
copy "AutoMudfish.exe" "%PROGRAMFILES%\\Auto Mudfish\\"

REM Create desktop shortcut
echo Creating desktop shortcut...
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\\Desktop\\Auto Mudfish.lnk'); $Shortcut.TargetPath = '%PROGRAMFILES%\\Auto Mudfish\\AutoMudfish.exe'; $Shortcut.Save()"

REM Create start menu shortcut
echo Creating start menu shortcut...
if not exist "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Auto Mudfish" mkdir "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Auto Mudfish"
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Auto Mudfish\\Auto Mudfish.lnk'); $Shortcut.TargetPath = '%PROGRAMFILES%\\Auto Mudfish\\AutoMudfish.exe'; $Shortcut.Save()"

echo Installation completed!
echo You can now run Auto Mudfish from the desktop shortcut or start menu.
pause
'''
    
    with open('dist/install.bat', 'w') as f:
        f.write(installer_content)
    
    print("Created installer script: dist/install.bat")


def create_readme():
    """Create a README for the executable distribution."""
    readme_content = '''# Auto Mudfish VPN - Executable Distribution

## Installation

1. Run `install.bat` as Administrator to install Auto Mudfish
2. The application will be installed to `C:\\Program Files\\Auto Mudfish\\`
3. Desktop and Start Menu shortcuts will be created

## Usage

1. Launch Auto Mudfish from the desktop shortcut or Start Menu
2. Go to the "Credentials" tab to set up your Mudfish username and password
3. Use the "Main" tab to connect/disconnect from Mudfish VPN
4. Check the "Logs" tab for detailed operation information

## Features

- **Secure Credential Storage**: Your credentials are encrypted using Windows DPAPI
- **One-Click Connection**: Connect to Mudfish VPN with a single click
- **Headless Operation**: No browser windows pop up during operation
- **Status Monitoring**: Check connection status and view detailed logs
- **Automatic ChromeDriver Management**: Downloads and manages ChromeDriver automatically

## Requirements

- Windows 10/11
- Chrome browser installed
- Internet connection

## Troubleshooting

- If you encounter ChromeDriver issues, try the "Cleanup Old ChromeDrivers" option in Settings
- Check the Logs tab for detailed error information
- Ensure Chrome browser is installed and up to date

## Support

For issues and questions, please check the project repository on GitHub.
'''
    
    with open('dist/README_EXECUTABLE.txt', 'w') as f:
        f.write(readme_content)
    
    print("Created README: dist/README_EXECUTABLE.txt")


def main():
    """Main build process."""
    print("Auto Mudfish Executable Builder")
    print("==============================")
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print(f"PyInstaller version: {PyInstaller.__version__}")
    except ImportError:
        print("PyInstaller not found. Installing...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyinstaller'])
    
    # Clean previous builds
    clean_build_dirs()
    
    # Build executable
    if build_executable():
        print("\nBuild successful!")
        
        # Create additional files
        create_installer_script()
        create_readme()
        
        print("\nFiles created:")
        print("- dist/AutoMudfish.exe (main executable)")
        print("- dist/install.bat (installer script)")
        print("- dist/README_EXECUTABLE.txt (user documentation)")
        
        print("\nTo distribute:")
        print("1. Copy the entire 'dist' folder contents")
        print("2. Include install.bat and README_EXECUTABLE.txt")
        print("3. Users can run install.bat as Administrator to install")
        
    else:
        print("\nBuild failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
