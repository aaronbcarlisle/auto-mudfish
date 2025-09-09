#!/usr/bin/env python3
"""
Simple Auto Mudfish VPN Installer

A lightweight installer that creates a basic installation without
requiring all the heavy dependencies.
"""

import sys
import os
import shutil
import subprocess
import tempfile
import zipfile
import urllib.request
from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QProgressBar, QTextEdit, QTabWidget,
    QGroupBox, QCheckBox, QMessageBox, QFileDialog, QLineEdit,
    QFormLayout, QSplitter
)
from PyQt6.QtCore import QThread, pyqtSignal, QTimer, Qt
from PyQt6.QtGui import QFont, QPixmap, QIcon


class SimpleInstallerWorker(QThread):
    """Worker thread for simple installation process."""
    
    progress_update = pyqtSignal(int)
    status_update = pyqtSignal(str)
    log_message = pyqtSignal(str)
    installation_complete = pyqtSignal(bool, str)
    
    def __init__(self, install_path: str, create_desktop_shortcut: bool, 
                 create_start_menu: bool):
        super().__init__()
        self.install_path = install_path
        self.create_desktop_shortcut = create_desktop_shortcut
        self.create_start_menu = create_start_menu
        
    def run(self):
        """Execute the installation process."""
        try:
            self.status_update.emit("Starting installation...")
            self.progress_update.emit(5)
            
            # Step 1: Create installation directory
            self.log_message.emit(f"Creating installation directory: {self.install_path}")
            os.makedirs(self.install_path, exist_ok=True)
            self.progress_update.emit(20)
            
            # Step 2: Copy application files
            self.status_update.emit("Copying application files...")
            self._copy_application_files()
            self.progress_update.emit(60)
            
            # Step 3: Create shortcuts
            self.status_update.emit("Creating shortcuts...")
            if self.create_desktop_shortcut:
                self._create_desktop_shortcut()
            if self.create_start_menu:
                self._create_start_menu_shortcut()
            self.progress_update.emit(80)
            
            # Step 4: Create uninstaller
            self.status_update.emit("Creating uninstaller...")
            self._create_uninstaller()
            self.progress_update.emit(95)
            
            # Step 5: Create install info
            self.status_update.emit("Finalizing installation...")
            self._create_install_info()
            self.progress_update.emit(100)
            
            self.installation_complete.emit(True, "Installation completed successfully!")
            
        except Exception as e:
            self.log_message.emit(f"Installation error: {str(e)}")
            self.installation_complete.emit(False, f"Installation failed: {str(e)}")
    
    def _copy_application_files(self):
        """Copy all application files to installation directory."""
        # Get the source directory (where the installer is running from)
        source_dir = Path(__file__).parent.parent.parent  # Go up to project root
        
        # Files to copy
        files_to_copy = [
            "main.py",
            "gui.py", 
            "launcher.py",
            "requirements.txt",
            "README.md"
        ]
        
        # Directories to copy
        dirs_to_copy = [
            "src",
            "scripts",
            "tests",
            "docs",
            "assets"
        ]
        
        # Copy files
        for file_name in files_to_copy:
            src_file = source_dir / file_name
            if src_file.exists():
                dst_file = Path(self.install_path) / file_name
                shutil.copy2(src_file, dst_file)
                self.log_message.emit(f"Copied {file_name}")
        
        # Copy directories
        for dir_name in dirs_to_copy:
            src_dir_path = source_dir / dir_name
            if src_dir_path.exists():
                dst_dir_path = Path(self.install_path) / dir_name
                if dst_dir_path.exists():
                    shutil.rmtree(dst_dir_path)
                shutil.copytree(src_dir_path, dst_dir_path)
                self.log_message.emit(f"Copied directory {dir_name}")
    
    def _create_desktop_shortcut(self):
        """Create desktop shortcut."""
        try:
            desktop_path = Path.home() / "Desktop"
            shortcut_path = desktop_path / "Auto Mudfish VPN.lnk"
            
            # Create shortcut using PowerShell
            target_path = Path(self.install_path) / "gui.py"
            
            ps_script = f'''
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
$Shortcut.TargetPath = "python"
$Shortcut.Arguments = '"{target_path}"'
$Shortcut.WorkingDirectory = "{self.install_path}"
$Shortcut.Description = "Auto Mudfish VPN - Connect to Mudfish VPN easily"
$Shortcut.Save()
'''
            
            subprocess.run(["powershell", "-Command", ps_script], check=True)
            self.log_message.emit("Created desktop shortcut")
        except Exception as e:
            self.log_message.emit(f"Failed to create desktop shortcut: {e}")
    
    def _create_start_menu_shortcut(self):
        """Create start menu shortcut."""
        try:
            start_menu_path = Path.home() / "AppData" / "Roaming" / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Auto Mudfish"
            start_menu_path.mkdir(parents=True, exist_ok=True)
            
            shortcut_path = start_menu_path / "Auto Mudfish VPN.lnk"
            target_path = Path(self.install_path) / "gui.py"
            
            ps_script = f'''
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
$Shortcut.TargetPath = "python"
$Shortcut.Arguments = '"{target_path}"'
$Shortcut.WorkingDirectory = "{self.install_path}"
$Shortcut.Description = "Auto Mudfish VPN - Connect to Mudfish VPN easily"
$Shortcut.Save()
'''
            
            subprocess.run(["powershell", "-Command", ps_script], check=True)
            self.log_message.emit("Created start menu shortcut")
        except Exception as e:
            self.log_message.emit(f"Failed to create start menu shortcut: {e}")
    
    def _create_uninstaller(self):
        """Create uninstaller script."""
        uninstaller_content = f'''@echo off
echo Auto Mudfish VPN Uninstaller
echo =============================

echo Removing Auto Mudfish VPN...

REM Remove shortcuts
if exist "%USERPROFILE%\\Desktop\\Auto Mudfish VPN.lnk" del "%USERPROFILE%\\Desktop\\Auto Mudfish VPN.lnk"
if exist "%USERPROFILE%\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Auto Mudfish\\Auto Mudfish VPN.lnk" del "%USERPROFILE%\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Auto Mudfish\\Auto Mudfish VPN.lnk"
if exist "%USERPROFILE%\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Auto Mudfish" rmdir "%USERPROFILE%\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Auto Mudfish"

REM Remove installation directory
if exist "{self.install_path}" rmdir /s /q "{self.install_path}"

echo Uninstallation completed!
pause
'''
        
        uninstaller_path = Path(self.install_path) / "uninstall.bat"
        with open(uninstaller_path, 'w') as f:
            f.write(uninstaller_content)
        
        self.log_message.emit("Created uninstaller")
    
    def _create_install_info(self):
        """Create installation information file."""
        install_info = {
            "version": "1.0.0",
            "install_path": self.install_path,
            "install_date": str(Path().cwd()),
            "desktop_shortcut": self.create_desktop_shortcut,
            "start_menu": self.create_start_menu
        }
        
        import json
        info_path = Path(self.install_path) / "install_info.json"
        with open(info_path, 'w') as f:
            json.dump(install_info, f, indent=2)
        
        self.log_message.emit("Created installation info")


class SimpleInstallerGUI(QMainWindow):
    """Simple installer GUI window."""
    
    def __init__(self):
        super().__init__()
        self.worker = None
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the user interface."""
        self.setWindowTitle("Auto Mudfish VPN - Simple Installer")
        self.setGeometry(100, 100, 600, 500)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Title
        title_label = QLabel("Auto Mudfish VPN Installer")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Welcome message
        welcome_text = QLabel("""
        <p>This installer will install Auto Mudfish VPN to your system.</p>
        
        <h3>What will be installed:</h3>
        <ul>
        <li>Auto Mudfish VPN application files</li>
        <li>Desktop shortcut (optional)</li>
        <li>Start menu entry (optional)</li>
        <li>Uninstaller</li>
        </ul>
        
        <p><b>Note:</b> You will need Python 3.8+ installed to run the application.</p>
        """)
        welcome_text.setWordWrap(True)
        main_layout.addWidget(welcome_text)
        
        # Installation path
        path_group = QGroupBox("Installation Path")
        path_layout = QHBoxLayout(path_group)
        
        self.install_path_edit = QLineEdit()
        self.install_path_edit.setText(str(Path.home() / "AppData" / "Local" / "Programs" / "Auto Mudfish"))
        path_layout.addWidget(self.install_path_edit)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_install_path)
        path_layout.addWidget(browse_btn)
        
        main_layout.addWidget(path_group)
        
        # Installation options
        options_group = QGroupBox("Installation Options")
        options_layout = QVBoxLayout(options_group)
        
        self.desktop_shortcut_cb = QCheckBox("Create desktop shortcut")
        self.desktop_shortcut_cb.setChecked(True)
        options_layout.addWidget(self.desktop_shortcut_cb)
        
        self.start_menu_cb = QCheckBox("Create start menu entry")
        self.start_menu_cb.setChecked(True)
        options_layout.addWidget(self.start_menu_cb)
        
        main_layout.addWidget(options_group)
        
        # Progress section
        progress_group = QGroupBox("Installation Progress")
        progress_layout = QVBoxLayout(progress_group)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        progress_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Ready to install")
        self.status_label.setFont(QFont("Arial", 10))
        progress_layout.addWidget(self.status_label)
        
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setFont(QFont("Consolas", 8))
        self.log_display.setMaximumHeight(150)
        progress_layout.addWidget(self.log_display)
        
        main_layout.addWidget(progress_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.install_btn = QPushButton("Install")
        self.install_btn.clicked.connect(self.start_installation)
        button_layout.addWidget(self.install_btn)
        
        button_layout.addStretch()
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.close)
        button_layout.addWidget(self.cancel_btn)
        
        main_layout.addLayout(button_layout)
        
    def browse_install_path(self):
        """Browse for installation path."""
        path = QFileDialog.getExistingDirectory(self, "Select Installation Directory")
        if path:
            self.install_path_edit.setText(path)
    
    def start_installation(self):
        """Start the installation process."""
        self.install_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        
        # Start installation worker
        self.worker = SimpleInstallerWorker(
            install_path=self.install_path_edit.text(),
            create_desktop_shortcut=self.desktop_shortcut_cb.isChecked(),
            create_start_menu=self.start_menu_cb.isChecked()
        )
        
        self.worker.progress_update.connect(self.progress_bar.setValue)
        self.worker.status_update.connect(self.status_label.setText)
        self.worker.log_message.connect(self.log_display.append)
        self.worker.installation_complete.connect(self.on_installation_complete)
        
        self.worker.start()
    
    def on_installation_complete(self, success, message):
        """Handle installation completion."""
        self.progress_bar.setVisible(False)
        
        if success:
            self.status_label.setText("Installation completed successfully!")
            self.install_btn.setText("Close")
            self.install_btn.setEnabled(True)
            self.install_btn.clicked.connect(self.close)
            
            QMessageBox.information(self, "Installation Complete", 
                                  "Auto Mudfish VPN has been installed successfully!\n\n"
                                  "You can now launch it from the desktop shortcut or start menu.\n\n"
                                  "Note: Make sure you have Python 3.8+ installed to run the application.")
        else:
            self.status_label.setText("Installation failed!")
            self.install_btn.setText("Retry")
            self.install_btn.setEnabled(True)
            self.install_btn.clicked.connect(self.start_installation)
            QMessageBox.critical(self, "Installation Failed", message)


def main():
    """Main entry point for the installer."""
    app = QApplication(sys.argv)
    app.setApplicationName("Auto Mudfish VPN Installer")
    app.setApplicationVersion("1.0.0")
    
    # Create and show installer window
    installer = SimpleInstallerGUI()
    installer.show()
    
    # Start event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
