#!/usr/bin/env python3
"""
Build script for creating the Auto Mudfish VPN installer executable.

This script uses PyInstaller to create a standalone installer executable
that users can download and run to install Auto Mudfish VPN.
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


def build_installer():
    """Build the installer executable using PyInstaller."""
    print("Building Auto Mudfish VPN Installer...")
    
    # PyInstaller command for installer
    cmd = [
        'pyinstaller',
        '--onefile',  # Create a single executable file
        '--windowed',  # No console window (GUI only)
        '--name=AutoMudfishInstaller',
        '--icon=../assets/icon.ico',  # Application icon
        '--add-data=../src;src',  # Include the source code
        '--add-data=../scripts;scripts',  # Include scripts
        '--add-data=../tests;tests',  # Include tests
        '--add-data=../docs;docs',  # Include docs
        '--add-data=../assets;assets',  # Include assets
        '--add-data=../main.py;.',  # Include main files
        '--add-data=../gui.py;.',
        '--add-data=../launcher.py;.',
        '--add-data=../requirements.txt;.',
        '--add-data=../README.md;.',
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
        '--exclude-module=tkinter',
        '--exclude-module=matplotlib',
        '--exclude-module=numpy',
        '--exclude-module=pandas',
        '../src/installer/installer.py'
    ]
    
    # Remove icon parameter if icon file doesn't exist
    if not os.path.exists('../assets/icon.ico'):
        cmd = [arg for arg in cmd if not arg.startswith('--icon')]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("Installer build completed successfully!")
        print(f"Installer location: {os.path.join('dist', 'AutoMudfishInstaller.exe')}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Installer build failed with error: {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        return False


def create_installer_package():
    """Create a complete installer package."""
    print("Creating installer package...")
    
    # Create package directory
    package_dir = Path("dist/installer_package")
    package_dir.mkdir(exist_ok=True)
    
    # Copy installer executable
    installer_exe = Path("dist/AutoMudfishInstaller.exe")
    if installer_exe.exists():
        shutil.copy2(installer_exe, package_dir / "AutoMudfishInstaller.exe")
        print("Copied installer executable")
    
    # Copy simple installer
    simple_installer = Path("../scripts/installer_simple.bat")
    if simple_installer.exists():
        shutil.copy2(simple_installer, package_dir / "install_simple.bat")
        print("Copied simple installer")
    
    # Create README for installer package
    readme_content = '''# Auto Mudfish VPN Installer Package

## Installation Options

### Option 1: Graphical Installer (Recommended)
1. Run `AutoMudfishInstaller.exe`
2. Follow the installation wizard
3. Choose installation options
4. Complete installation

### Option 2: Simple Installer
1. Run `install_simple.bat` as Administrator
2. Installation will proceed automatically
3. Application will be installed to Program Files

## What Gets Installed

- Auto Mudfish VPN application files
- Desktop shortcut (optional)
- Start menu entry (optional)
- Startup entry (optional)
- Uninstaller

## Requirements

- Windows 10/11
- Administrator privileges for installation
- Python 3.8+ (will be installed if needed)
- Chrome browser
- Internet connection

## After Installation

Launch Auto Mudfish VPN from:
- Desktop shortcut
- Start Menu
- Installation directory

## Uninstallation

To uninstall, run the uninstaller from the installation directory or use Windows Add/Remove Programs.

## Support

For issues and questions, please check the project repository on GitHub.
'''
    
    with open(package_dir / "README.txt", 'w') as f:
        f.write(readme_content)
    
    print(f"Installer package created: {package_dir}")
    return True


def main():
    """Main build process."""
    print("Auto Mudfish VPN Installer Builder")
    print("==================================")
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print(f"PyInstaller version: {PyInstaller.__version__}")
    except ImportError:
        print("PyInstaller not found. Installing...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyinstaller'])
    
    # Clean previous builds
    clean_build_dirs()
    
    # Build installer
    if build_installer():
        print("\nInstaller build successful!")
        
        # Create installer package
        if create_installer_package():
            print("\nInstaller package created successfully!")
            
            print("\nFiles created:")
            print("- dist/AutoMudfishInstaller.exe (graphical installer)")
            print("- dist/installer_package/ (complete package)")
            print("  - AutoMudfishInstaller.exe")
            print("  - install_simple.bat")
            print("  - README.txt")
            
            print("\nTo distribute:")
            print("1. Share the entire 'dist/installer_package' folder")
            print("2. Users can run either installer")
            print("3. Graphical installer provides more options")
            print("4. Simple installer is quick and automatic")
            
        else:
            print("\nFailed to create installer package!")
            sys.exit(1)
        
    else:
        print("\nInstaller build failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
