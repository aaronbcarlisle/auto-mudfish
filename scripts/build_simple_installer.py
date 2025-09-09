#!/usr/bin/env python3
"""
Build script for creating a simple Auto Mudfish VPN installer executable.

This script uses PyInstaller to create a lightweight installer executable
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


def build_simple_installer():
    """Build the simple installer executable using PyInstaller."""
    print("Building Simple Auto Mudfish VPN Installer...")
    
    # PyInstaller command for simple installer
    cmd = [
        'pyinstaller',
        '--onefile',  # Create a single executable file
        '--windowed',  # No console window (GUI only)
        '--name=AutoMudfishSimpleInstaller',
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
        '--exclude-module=selenium',
        '--exclude-module=requests',
        '--exclude-module=beautifulsoup4',
        '--exclude-module=psutil',
        '--exclude-module=win32crypt',
        '--exclude-module=win32api',
        '--exclude-module=get_chrome_driver',
        '--exclude-module=tkinter',
        '--exclude-module=matplotlib',
        '--exclude-module=numpy',
        '--exclude-module=pandas',
        '--exclude-module=trio',
        '--exclude-module=trio_websocket',
        '--exclude-module=h11',
        '--exclude-module=wsproto',
        '--exclude-module=exceptiongroup',
        '--exclude-module=cffi',
        '--exclude-module=pycparser',
        '--exclude-module=sortedcontainers',
        '--exclude-module=outcome',
        '--exclude-module=sniffio',
        '../src/installer/simple_installer.py'
    ]
    
    # Create icon if it doesn't exist
    if not os.path.exists('../assets/icon.ico'):
        print("Creating application icon...")
        try:
            import subprocess
            subprocess.run([sys.executable, 'create_mudfish_icon.py'], cwd='scripts', check=True)
        except:
            print("Warning: Could not create icon, proceeding without icon")
    
    # Add icon parameter if icon file exists
    if os.path.exists('../assets/icon.ico'):
        cmd.insert(-1, '--icon=../assets/icon.ico')
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("Simple installer build completed successfully!")
        print(f"Installer location: {os.path.join('dist', 'AutoMudfishSimpleInstaller.exe')}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Simple installer build failed with error: {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        return False


def create_installer_package():
    """Create a complete installer package."""
    print("Creating installer package...")
    
    # Create package directory
    package_dir = Path("dist/installer_package")
    package_dir.mkdir(exist_ok=True)
    
    # Copy simple installer executable
    installer_exe = Path("dist/AutoMudfishSimpleInstaller.exe")
    if installer_exe.exists():
        shutil.copy2(installer_exe, package_dir / "AutoMudfishSimpleInstaller.exe")
        print("Copied simple installer executable")
    
    # Copy simple installer batch
    simple_installer = Path("../scripts/installer_simple.bat")
    if simple_installer.exists():
        shutil.copy2(simple_installer, package_dir / "install_simple.bat")
        print("Copied simple installer batch")
    
    # Create README for installer package
    readme_content = '''# Auto Mudfish VPN Installer Package

## Installation Options

### Option 1: Simple Graphical Installer (Recommended)
1. Run `AutoMudfishSimpleInstaller.exe`
2. Choose installation directory
3. Select shortcuts to create
4. Click Install

### Option 2: Simple Batch Installer
1. Run `install_simple.bat` as Administrator
2. Installation will proceed automatically
3. Application will be installed to Program Files

## What Gets Installed

- Auto Mudfish VPN application files
- Desktop shortcut (optional)
- Start menu entry (optional)
- Uninstaller

## Requirements

- Windows 10/11
- Administrator privileges for installation
- Python 3.8+ (must be installed separately)
- Chrome browser
- Internet connection

## After Installation

Launch Auto Mudfish VPN from:
- Desktop shortcut
- Start Menu
- Installation directory

## Uninstallation

To uninstall, run the uninstaller from the installation directory.

## Support

For issues and questions, please check the project repository on GitHub.
'''
    
    with open(package_dir / "README.txt", 'w') as f:
        f.write(readme_content)
    
    print(f"Installer package created: {package_dir}")
    return True


def main():
    """Main build process."""
    print("Auto Mudfish VPN Simple Installer Builder")
    print("=========================================")
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print(f"PyInstaller version: {PyInstaller.__version__}")
    except ImportError:
        print("PyInstaller not found. Installing...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyinstaller'])
    
    # Clean previous builds
    clean_build_dirs()
    
    # Build simple installer
    if build_simple_installer():
        print("\nSimple installer build successful!")
        
        # Create installer package
        if create_installer_package():
            print("\nInstaller package created successfully!")
            
            print("\nFiles created:")
            print("- dist/AutoMudfishSimpleInstaller.exe (simple graphical installer)")
            print("- dist/installer_package/ (complete package)")
            print("  - AutoMudfishSimpleInstaller.exe")
            print("  - install_simple.bat")
            print("  - README.txt")
            
            print("\nTo distribute:")
            print("1. Share the entire 'dist/installer_package' folder")
            print("2. Users can run either installer")
            print("3. Simple installer is lightweight and fast")
            print("4. Batch installer is quick and automatic")
            
        else:
            print("\nFailed to create installer package!")
            sys.exit(1)
        
    else:
        print("\nSimple installer build failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
