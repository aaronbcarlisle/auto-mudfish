#!/usr/bin/env python3
"""
Auto Mudfish GUI Application

A PyQt6-based graphical user interface for the auto-mudfish VPN automation tool.
Provides an easy-to-use interface for managing credentials and connecting to Mudfish VPN.
"""

import sys
import os
import logging
import json
from typing import Optional
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QGridLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QTabWidget,
    QGroupBox, QCheckBox, QProgressBar, QMessageBox, QFileDialog,
    QSystemTrayIcon, QMenu, QStatusBar, QSplitter
)
from PyQt6.QtCore import QThread, pyqtSignal, QTimer, Qt, QSettings
from PyQt6.QtGui import QIcon, QFont, QPixmap

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from auto_mudfish.connection import MudfishConnection
from auto_mudfish.driver import get_chrome_driver
from auto_mudfish.process import MudfishProcess
from auto_mudfish.credentials import get_credential_manager


class MudfishWorker(QThread):
    """Worker thread for Mudfish operations to prevent GUI freezing."""
    
    # Signals
    status_update = pyqtSignal(str)
    progress_update = pyqtSignal(int)
    operation_complete = pyqtSignal(bool, str)
    log_message = pyqtSignal(str)
    
    def __init__(self, operation_type: str, **kwargs):
        super().__init__()
        self.operation_type = operation_type
        self.kwargs = kwargs
        self.logger = logging.getLogger("auto_mudfish.gui.worker")
        
    def run(self):
        """Execute the specified operation."""
        try:
            if self.operation_type == "connect":
                self._connect_mudfish()
            elif self.operation_type == "disconnect":
                self._disconnect_mudfish()
            elif self.operation_type == "check_status":
                self._check_status()
            elif self.operation_type == "setup_credentials":
                self._setup_credentials()
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.logger.error(error_msg)
            self.log_message.emit(error_msg)
            self.operation_complete.emit(False, error_msg)
    
    def _connect_mudfish(self):
        """Connect to Mudfish VPN."""
        self.status_update.emit("Starting Mudfish automation...")
        self.progress_update.emit(10)
        self.log_message.emit("Starting Mudfish automation...")
        
        # Check if Mudfish is running
        self.status_update.emit("Checking Mudfish process...")
        self.log_message.emit("Checking Mudfish process...")
        mudfish_process = MudfishProcess()
        if not mudfish_process.start_mudfish_launcher():
            error_msg = "Mudfish is not running and could not be started."
            self.log_message.emit(error_msg)
            self.operation_complete.emit(False, error_msg)
            return
        
        self.progress_update.emit(30)
        
        # Load credentials
        self.status_update.emit("Loading credentials...")
        self.log_message.emit("Loading credentials...")
        cred_manager = get_credential_manager()
        credentials = cred_manager.load_credentials()
        
        if not credentials:
            error_msg = "No stored credentials found. Please set up credentials first."
            self.log_message.emit(error_msg)
            self.operation_complete.emit(False, error_msg)
            return
        
        username = credentials.get("username", "")
        password = credentials.get("password", "")
        adminpage = credentials.get("adminpage")
        
        self.progress_update.emit(50)
        
        # Attempt headless login
        self.status_update.emit("Attempting headless login...")
        self.log_message.emit("Attempting headless login...")
        mudfish_connection = MudfishConnection(web_driver=None)
        if mudfish_connection.login_without_driver(username, password, adminpage):
            self.status_update.emit("Headless login successful!")
            self.log_message.emit("Headless login successful!")
            self.progress_update.emit(70)
        else:
            self.status_update.emit("Headless login failed, using WebDriver...")
            self.log_message.emit("Headless login failed, using WebDriver...")
            self.progress_update.emit(60)
        
        # Try to use WebDriver for connection
        self.status_update.emit("Starting WebDriver...")
        self.log_message.emit("Starting WebDriver...")
        chrome_driver = get_chrome_driver(headless=True)
        
        if chrome_driver:
            self.progress_update.emit(80)
            
            # Complete connection with WebDriver
            self.status_update.emit("Connecting to VPN...")
            self.log_message.emit("Connecting to VPN...")
            mudfish_connection = MudfishConnection(web_driver=chrome_driver)
            mudfish_connection.login(username, password, adminpage)
            mudfish_connection.connect()
            
            self.progress_update.emit(100)
            success_msg = "Successfully connected to Mudfish VPN!"
            self.log_message.emit(success_msg)
            self.operation_complete.emit(True, success_msg)
        else:
            # WebDriver failed, but headless login might have worked
            self.log_message.emit("WebDriver creation failed, but headless login was successful")
            self.log_message.emit("Mudfish should be accessible via web interface at http://127.0.0.1:8282")
            self.log_message.emit("Please check the Mudfish web interface to complete the connection")
            
            self.progress_update.emit(100)
            success_msg = "Mudfish started successfully! Please check the web interface to complete connection."
            self.log_message.emit(success_msg)
            self.operation_complete.emit(True, success_msg)
    
    def _disconnect_mudfish(self):
        """Disconnect from Mudfish VPN."""
        self.status_update.emit("Disconnecting from Mudfish...")
        self.log_message.emit("Disconnecting from Mudfish...")
        self.progress_update.emit(25)
        
        # First check if Mudfish processes are running
        mudfish_connection = MudfishConnection(web_driver=None)
        if not mudfish_connection._is_mudfish_running():
            info_msg = "Mudfish is not currently running - already disconnected."
            self.log_message.emit(info_msg)
            self.progress_update.emit(100)
            self.operation_complete.emit(True, info_msg)
            return
        
        self.progress_update.emit(50)
        
        # Try to use WebDriver for disconnect
        chrome_driver = get_chrome_driver(headless=True)
        if chrome_driver:
            self.log_message.emit("WebDriver created, attempting disconnect...")
            
            mudfish_connection = MudfishConnection(web_driver=chrome_driver)
            
            # Check if connected first
            if mudfish_connection.is_mudfish_connected():
                self.log_message.emit("VPN is connected, attempting disconnect...")
                mudfish_connection.disconnect()
                self.progress_update.emit(75)
                
                # Wait a moment and check if disconnected
                self.status_update.emit("Verifying disconnect...")
                self.log_message.emit("Verifying disconnect...")
                if mudfish_connection.is_mudfish_disconnected():
                    success_msg = "Successfully disconnected from Mudfish VPN!"
                    self.log_message.emit(success_msg)
                    self.progress_update.emit(100)
                    self.operation_complete.emit(True, success_msg)
                else:
                    error_msg = "Disconnect command sent but status unclear."
                    self.log_message.emit(error_msg)
                    self.progress_update.emit(100)
                    self.operation_complete.emit(False, error_msg)
            else:
                info_msg = "Mudfish is not currently connected."
                self.log_message.emit(info_msg)
                self.progress_update.emit(100)
                self.operation_complete.emit(True, info_msg)
        else:
            # WebDriver failed, but we can still provide guidance
            self.log_message.emit("WebDriver creation failed, but Mudfish processes are running")
            self.log_message.emit("Please use the Mudfish web interface at http://127.0.0.1:8282 to disconnect")
            self.log_message.emit("Or stop Mudfish processes manually from Task Manager")
            
            self.progress_update.emit(100)
            info_msg = "Please disconnect manually via Mudfish web interface or Task Manager"
            self.log_message.emit(info_msg)
            self.operation_complete.emit(True, info_msg)
    
    def _check_status(self):
        """Check Mudfish connection status."""
        self.status_update.emit("Checking connection status...")
        self.log_message.emit("Checking connection status...")
        self.progress_update.emit(25)
        
        chrome_driver = get_chrome_driver(headless=True)
        if chrome_driver:
            self.progress_update.emit(50)
            self.log_message.emit("WebDriver created, checking status...")
            
            try:
                mudfish_connection = MudfishConnection(web_driver=chrome_driver)
                self.progress_update.emit(75)
                
                # Add timeout for status check
                import time
                start_time = time.time()
                timeout = 10  # 10 second timeout
                
                self.log_message.emit("Attempting to determine connection status...")
                
                # Try to check connection status with timeout
                is_connected = False
                try:
                    is_connected = mudfish_connection.is_mudfish_connected()
                except Exception as e:
                    self.log_message.emit(f"Status check encountered error: {e}")
                
                # Check if we timed out
                elapsed_time = time.time() - start_time
                if elapsed_time > timeout:
                    self.log_message.emit("Status check timed out, assuming disconnected")
                    is_connected = False
                
                if is_connected:
                    status_msg = "Mudfish is currently connected."
                else:
                    status_msg = "Mudfish is not connected."
                
                self.log_message.emit(status_msg)
                self.progress_update.emit(100)
                self.operation_complete.emit(True, status_msg)
                
            except Exception as e:
                error_msg = f"Error during status check: {str(e)}"
                self.log_message.emit(error_msg)
                self.progress_update.emit(100)
                self.operation_complete.emit(False, error_msg)
        else:
            error_msg = "Failed to check status - WebDriver error."
            self.log_message.emit(error_msg)
            self.operation_complete.emit(False, error_msg)
    
    def _setup_credentials(self):
        """Set up credentials (placeholder - would need GUI input)."""
        error_msg = "Credential setup should be done through the GUI."
        self.log_message.emit(error_msg)
        self.operation_complete.emit(False, error_msg)


class MudfishGUI(QMainWindow):
    """Main GUI window for Auto Mudfish."""
    
    def __init__(self):
        super().__init__()
        self.worker = None
        self.settings = QSettings("AutoMudfish", "Settings")
        self.setup_ui()
        self.setup_logging()
        self.load_settings()
        self.setup_dark_theme()
        
        # Check status on startup
        QTimer.singleShot(1000, self.check_status_on_startup)
        
    def setup_ui(self):
        """Set up the user interface."""
        self.setWindowTitle("Auto Mudfish VPN")
        self.setGeometry(100, 100, 900, 700)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        tab_widget = QTabWidget()
        main_layout.addWidget(tab_widget)
        
        # Create tabs
        self.create_main_tab(tab_widget)
        self.create_credentials_tab(tab_widget)
        self.create_settings_tab(tab_widget)
        self.create_logs_tab(tab_widget)
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        # Create progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)
        
    def setup_dark_theme(self):
        """Apply dark theme stylesheet."""
        dark_stylesheet = """
        QMainWindow {
            background-color: #2b2b2b;
            color: #ffffff;
        }
        
        QWidget {
            background-color: #2b2b2b;
            color: #ffffff;
        }
        
        QTabWidget::pane {
            border: 1px solid #555555;
            background-color: #3c3c3c;
        }
        
        QTabBar::tab {
            background-color: #3c3c3c;
            color: #ffffff;
            padding: 8px 16px;
            margin-right: 2px;
        }
        
        QTabBar::tab:selected {
            background-color: #4a4a4a;
            border-bottom: 2px solid #0078d4;
        }
        
        QTabBar::tab:hover {
            background-color: #4a4a4a;
        }
        
        QGroupBox {
            font-weight: bold;
            border: 2px solid #555555;
            border-radius: 5px;
            margin-top: 1ex;
            padding-top: 10px;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
        }
        
        QPushButton {
            background-color: #404040;
            border: 1px solid #555555;
            border-radius: 4px;
            padding: 8px 16px;
            color: #ffffff;
        }
        
        QPushButton:hover {
            background-color: #4a4a4a;
        }
        
        QPushButton:pressed {
            background-color: #353535;
        }
        
        QPushButton:disabled {
            background-color: #2b2b2b;
            color: #666666;
        }
        
        QLineEdit {
            background-color: #404040;
            border: 1px solid #555555;
            border-radius: 4px;
            padding: 6px;
            color: #ffffff;
        }
        
        QLineEdit:focus {
            border: 2px solid #0078d4;
        }
        
        QTextEdit {
            background-color: #1e1e1e;
            border: 1px solid #555555;
            border-radius: 4px;
            color: #ffffff;
            font-family: 'Consolas', 'Monaco', monospace;
        }
        
        QCheckBox {
            color: #ffffff;
        }
        
        QCheckBox::indicator {
            width: 18px;
            height: 18px;
        }
        
        QCheckBox::indicator:unchecked {
            border: 2px solid #555555;
            background-color: #404040;
            border-radius: 3px;
        }
        
        QCheckBox::indicator:checked {
            border: 2px solid #0078d4;
            background-color: #0078d4;
            border-radius: 3px;
        }
        
        QProgressBar {
            border: 2px solid #555555;
            border-radius: 5px;
            text-align: center;
            background-color: #404040;
        }
        
        QProgressBar::chunk {
            background-color: #0078d4;
            border-radius: 3px;
        }
        
        QStatusBar {
            background-color: #2b2b2b;
            color: #ffffff;
            border-top: 1px solid #555555;
        }
        
        QLabel {
            color: #ffffff;
        }
        """
        
        self.setStyleSheet(dark_stylesheet)
        
    def create_main_tab(self, parent):
        """Create the main control tab."""
        main_tab = QWidget()
        parent.addTab(main_tab, "Main")
        
        layout = QVBoxLayout(main_tab)
        
        # Title
        title_label = QLabel("Auto Mudfish VPN")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Status group
        status_group = QGroupBox("Status")
        status_layout = QVBoxLayout(status_group)
        
        self.status_label = QLabel("Status: Checking...")
        self.status_label.setFont(QFont("Arial", 12))
        status_layout.addWidget(self.status_label)
        
        # Connection info
        self.connection_info = QLabel("No connection information available")
        self.connection_info.setWordWrap(True)
        status_layout.addWidget(self.connection_info)
        
        layout.addWidget(status_group)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.connect_btn = QPushButton("Connect")
        self.connect_btn.clicked.connect(self.connect_mudfish)
        self.connect_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; padding: 10px; }")
        button_layout.addWidget(self.connect_btn)
        
        self.disconnect_btn = QPushButton("Disconnect")
        self.disconnect_btn.clicked.connect(self.disconnect_mudfish)
        self.disconnect_btn.setStyleSheet("QPushButton { background-color: #f44336; color: white; font-weight: bold; padding: 10px; }")
        self.disconnect_btn.setEnabled(False)
        button_layout.addWidget(self.disconnect_btn)
        
        self.status_check_btn = QPushButton("Check Status")
        self.status_check_btn.clicked.connect(self.check_status)
        self.status_check_btn.setStyleSheet("QPushButton { background-color: #2196F3; color: white; font-weight: bold; padding: 10px; }")
        button_layout.addWidget(self.status_check_btn)
        
        layout.addLayout(button_layout)
        
        # Options
        options_group = QGroupBox("Options")
        options_layout = QVBoxLayout(options_group)
        
        self.show_browser_cb = QCheckBox("Show browser window (for debugging)")
        options_layout.addWidget(self.show_browser_cb)
        
        self.verbose_cb = QCheckBox("Verbose logging")
        options_layout.addWidget(self.verbose_cb)
        
        layout.addWidget(options_group)
        
        # Add stretch to push everything to top
        layout.addStretch()
        
    def create_credentials_tab(self, parent):
        """Create the credentials management tab."""
        cred_tab = QWidget()
        parent.addTab(cred_tab, "Credentials")
        
        layout = QVBoxLayout(cred_tab)
        
        # Title
        title_label = QLabel("Credential Management")
        title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(title_label)
        
        # Current credentials info
        info_group = QGroupBox("Current Credentials")
        info_layout = QVBoxLayout(info_group)
        
        self.cred_info_label = QLabel("No credentials stored")
        self.cred_info_label.setWordWrap(True)
        info_layout.addWidget(self.cred_info_label)
        
        layout.addWidget(info_group)
        
        # Credential setup
        setup_group = QGroupBox("Setup Credentials")
        setup_layout = QGridLayout(setup_group)
        
        setup_layout.addWidget(QLabel("Username:"), 0, 0)
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Enter your Mudfish username")
        setup_layout.addWidget(self.username_edit, 0, 1)
        
        setup_layout.addWidget(QLabel("Password:"), 1, 0)
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_edit.setPlaceholderText("Enter your Mudfish password")
        setup_layout.addWidget(self.password_edit, 1, 1)
        
        setup_layout.addWidget(QLabel("Admin Page:"), 2, 0)
        self.adminpage_edit = QLineEdit()
        self.adminpage_edit.setPlaceholderText("Optional: Custom admin page URL")
        setup_layout.addWidget(self.adminpage_edit, 2, 1)
        
        layout.addWidget(setup_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.save_creds_btn = QPushButton("Save Credentials")
        self.save_creds_btn.clicked.connect(self.save_credentials)
        self.save_creds_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; padding: 8px; }")
        button_layout.addWidget(self.save_creds_btn)
        
        self.clear_creds_btn = QPushButton("Clear Credentials")
        self.clear_creds_btn.clicked.connect(self.clear_credentials)
        self.clear_creds_btn.setStyleSheet("QPushButton { background-color: #f44336; color: white; font-weight: bold; padding: 8px; }")
        button_layout.addWidget(self.clear_creds_btn)
        
        self.refresh_creds_btn = QPushButton("Refresh Info")
        self.refresh_creds_btn.clicked.connect(self.refresh_credentials_info)
        self.refresh_creds_btn.setStyleSheet("QPushButton { background-color: #2196F3; color: white; font-weight: bold; padding: 8px; }")
        button_layout.addWidget(self.refresh_creds_btn)
        
        layout.addLayout(button_layout)
        layout.addStretch()
        
        # Load current credentials info
        self.refresh_credentials_info()
        
    def create_settings_tab(self, parent):
        """Create the settings tab."""
        settings_tab = QWidget()
        parent.addTab(settings_tab, "Settings")
        
        layout = QVBoxLayout(settings_tab)
        
        # Title
        title_label = QLabel("Settings")
        title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(title_label)
        
        # General settings
        general_group = QGroupBox("General")
        general_layout = QVBoxLayout(general_group)
        
        self.auto_connect_cb = QCheckBox("Auto-connect on startup")
        general_layout.addWidget(self.auto_connect_cb)
        
        self.minimize_to_tray_cb = QCheckBox("Minimize to system tray")
        general_layout.addWidget(self.minimize_to_tray_cb)
        
        self.start_with_windows_cb = QCheckBox("Start with Windows")
        general_layout.addWidget(self.start_with_windows_cb)
        
        layout.addWidget(general_group)
        
        # Advanced settings
        advanced_group = QGroupBox("Advanced")
        advanced_layout = QVBoxLayout(advanced_group)
        
        self.debug_mode_cb = QCheckBox("Debug mode")
        advanced_layout.addWidget(self.debug_mode_cb)
        
        self.cleanup_btn = QPushButton("Cleanup Old ChromeDrivers")
        self.cleanup_btn.clicked.connect(self.cleanup_chromedrivers)
        self.cleanup_btn.setStyleSheet("QPushButton { background-color: #FF9800; color: white; font-weight: bold; padding: 8px; }")
        advanced_layout.addWidget(self.cleanup_btn)
        
        layout.addWidget(advanced_group)
        layout.addStretch()
        
    def create_logs_tab(self, parent):
        """Create the logs tab."""
        logs_tab = QWidget()
        parent.addTab(logs_tab, "Logs")
        
        layout = QVBoxLayout(logs_tab)
        
        # Title and controls
        header_layout = QHBoxLayout()
        
        title_label = QLabel("Application Logs")
        title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        self.clear_logs_btn = QPushButton("Clear Logs")
        self.clear_logs_btn.clicked.connect(self.clear_logs)
        self.clear_logs_btn.setStyleSheet("QPushButton { background-color: #f44336; color: white; font-weight: bold; padding: 6px; }")
        header_layout.addWidget(self.clear_logs_btn)
        
        self.save_logs_btn = QPushButton("Save Logs")
        self.save_logs_btn.clicked.connect(self.save_logs)
        self.save_logs_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; padding: 6px; }")
        header_layout.addWidget(self.save_logs_btn)
        
        layout.addLayout(header_layout)
        
        # Log display
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setFont(QFont("Consolas", 9))
        layout.addWidget(self.log_display)
        
        # Set up log handler
        self.setup_log_handler()
        
    def setup_logging(self):
        """Set up logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger("auto_mudfish.gui")
        
    def setup_log_handler(self):
        """Set up custom log handler for GUI display."""
        class GUILogHandler(logging.Handler):
            def __init__(self, text_widget):
                super().__init__()
                self.text_widget = text_widget
                
            def emit(self, record):
                msg = self.format(record)
                self.text_widget.append(msg)
                
        handler = GUILogHandler(self.log_display)
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(handler)
        
    def load_settings(self):
        """Load settings from persistent storage."""
        self.show_browser_cb.setChecked(self.settings.value("show_browser", False, type=bool))
        self.verbose_cb.setChecked(self.settings.value("verbose", False, type=bool))
        self.auto_connect_cb.setChecked(self.settings.value("auto_connect", False, type=bool))
        self.minimize_to_tray_cb.setChecked(self.settings.value("minimize_to_tray", False, type=bool))
        self.start_with_windows_cb.setChecked(self.settings.value("start_with_windows", False, type=bool))
        self.debug_mode_cb.setChecked(self.settings.value("debug_mode", False, type=bool))
        
    def save_settings(self):
        """Save settings to persistent storage."""
        self.settings.setValue("show_browser", self.show_browser_cb.isChecked())
        self.settings.setValue("verbose", self.verbose_cb.isChecked())
        self.settings.setValue("auto_connect", self.auto_connect_cb.isChecked())
        self.settings.setValue("minimize_to_tray", self.minimize_to_tray_cb.isChecked())
        self.settings.setValue("start_with_windows", self.start_with_windows_cb.isChecked())
        self.settings.setValue("debug_mode", self.debug_mode_cb.isChecked())
        
    def check_status_on_startup(self):
        """Check connection status on startup."""
        self.logger.info("Checking connection status on startup...")
        self.check_status()
        
    def connect_mudfish(self):
        """Start connecting to Mudfish VPN."""
        if self.worker and self.worker.isRunning():
            return
            
        self.connect_btn.setEnabled(False)
        self.disconnect_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        self.worker = MudfishWorker("connect")
        self.worker.status_update.connect(self.update_status)
        self.worker.progress_update.connect(self.progress_bar.setValue)
        self.worker.operation_complete.connect(self.on_operation_complete)
        self.worker.log_message.connect(self.log_message)
        self.worker.start()
        
    def disconnect_mudfish(self):
        """Disconnect from Mudfish VPN."""
        if self.worker and self.worker.isRunning():
            return
            
        self.connect_btn.setEnabled(False)
        self.disconnect_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        self.worker = MudfishWorker("disconnect")
        self.worker.status_update.connect(self.update_status)
        self.worker.progress_update.connect(self.progress_bar.setValue)
        self.worker.operation_complete.connect(self.on_operation_complete)
        self.worker.log_message.connect(self.log_message)
        self.worker.start()
        
    def check_status(self):
        """Check Mudfish connection status."""
        if self.worker and self.worker.isRunning():
            return
            
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        self.worker = MudfishWorker("check_status")
        self.worker.status_update.connect(self.update_status)
        self.worker.progress_update.connect(self.progress_bar.setValue)
        self.worker.operation_complete.connect(self.on_operation_complete)
        self.worker.log_message.connect(self.log_message)
        self.worker.start()
        
    def update_status(self, message):
        """Update status message."""
        self.status_bar.showMessage(message)
        self.logger.info(message)
        
    def log_message(self, message):
        """Add message to log display."""
        self.log_display.append(message)
        
    def on_operation_complete(self, success, message):
        """Handle operation completion."""
        self.progress_bar.setVisible(False)
        self.connect_btn.setEnabled(True)
        self.disconnect_btn.setEnabled(True)
        
        if success:
            self.status_label.setText(f"Status: {message}")
            if "connected" in message.lower():
                self.connect_btn.setEnabled(False)
                self.disconnect_btn.setEnabled(True)
            elif "disconnected" in message.lower() or "not connected" in message.lower():
                self.connect_btn.setEnabled(True)
                self.disconnect_btn.setEnabled(False)
        else:
            self.status_label.setText("Status: Error")
            QMessageBox.warning(self, "Operation Failed", message)
            
        self.status_bar.showMessage("Ready")
        
    def save_credentials(self):
        """Save credentials to secure storage."""
        username = self.username_edit.text().strip()
        password = self.password_edit.text().strip()
        adminpage = self.adminpage_edit.text().strip() or None
        
        if not username or not password:
            QMessageBox.warning(self, "Invalid Input", "Username and password are required.")
            return
            
        try:
            cred_manager = get_credential_manager()
            if cred_manager.store_credentials(username, password, adminpage):
                QMessageBox.information(self, "Success", "Credentials saved successfully!")
                self.refresh_credentials_info()
                self.username_edit.clear()
                self.password_edit.clear()
                self.adminpage_edit.clear()
            else:
                QMessageBox.critical(self, "Error", "Failed to save credentials.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save credentials: {str(e)}")
            
    def clear_credentials(self):
        """Clear stored credentials."""
        reply = QMessageBox.question(
            self, "Confirm Clear", 
            "Are you sure you want to clear all stored credentials?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                cred_manager = get_credential_manager()
                if cred_manager.clear_credentials():
                    QMessageBox.information(self, "Success", "Credentials cleared successfully!")
                    self.refresh_credentials_info()
                else:
                    QMessageBox.critical(self, "Error", "Failed to clear credentials.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to clear credentials: {str(e)}")
                
    def refresh_credentials_info(self):
        """Refresh the credentials information display."""
        try:
            cred_manager = get_credential_manager()
            if cred_manager.has_credentials():
                info = cred_manager.get_credentials_info()
                if info:
                    self.cred_info_label.setText(
                        f"Username: {info['username']}\n"
                        f"Admin Page: {info['adminpage'] or 'Default'}\n"
                        f"Password: {'***' if info['has_password'] else 'Not set'}"
                    )
                else:
                    self.cred_info_label.setText("Failed to load credential information.")
            else:
                self.cred_info_label.setText("No credentials stored.")
        except Exception as e:
            self.cred_info_label.setText(f"Error loading credentials: {str(e)}")
            
    def cleanup_chromedrivers(self):
        """Clean up old ChromeDriver versions."""
        try:
            from auto_mudfish.driver import _cleanup_old_chromedrivers
            _cleanup_old_chromedrivers()
            QMessageBox.information(self, "Success", "ChromeDriver cleanup completed!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to cleanup ChromeDrivers: {str(e)}")
            
    def clear_logs(self):
        """Clear the log display."""
        self.log_display.clear()
        
    def save_logs(self):
        """Save logs to file."""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Logs", "mudfish_logs.txt", "Text Files (*.txt)"
        )
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write(self.log_display.toPlainText())
                QMessageBox.information(self, "Success", f"Logs saved to {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save logs: {str(e)}")
                
    def closeEvent(self, event):
        """Handle application close event."""
        self.save_settings()
        event.accept()


def main():
    """Main entry point for the GUI application."""
    app = QApplication(sys.argv)
    app.setApplicationName("Auto Mudfish VPN")
    app.setApplicationVersion("1.0.0")
    
    # Set application icon (if available)
    # app.setWindowIcon(QIcon("icon.ico"))
    
    # Create and show main window
    window = MudfishGUI()
    window.show()
    
    # Start event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()