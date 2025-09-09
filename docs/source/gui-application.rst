GUI Application
===============

The Auto Mudfish GUI provides an intuitive interface for managing VPN connections with secure credential storage and comprehensive monitoring.

Launching the GUI
-----------------

.. code-block:: bash

   # Launch GUI (requires administrator privileges)
   python src/gui/gui.py

   # OR use the provided PowerShell script
   run_as_admin.ps1

**Important:** The GUI requires administrator privileges to launch Mudfish.

Interface Overview
------------------

The GUI consists of four main tabs:

Main Tab
--------

Connection Controls
~~~~~~~~~~~~~~~~~~~

- **Connect Button**: Establishes VPN connection
- **Disconnect Button**: Terminates VPN connection  
- **Check Status Button**: Verifies current connection status

Status Display
~~~~~~~~~~~~~~

- **Connection Status**: Real-time connection information
- **Visual Indicators**: Color-coded status indicators
- **Status Details**: Detailed connection information

Options
~~~~~~~

- **Show Browser Window**: Display browser during operation (for debugging)
- **Verbose Logging**: Enable detailed logging output

Credentials Tab
---------------

Credential Management
~~~~~~~~~~~~~~~~~~~~~

- **Username Field**: Enter your Mudfish username
- **Password Field**: Enter your Mudfish password
- **Save Credentials**: Store credentials securely
- **Clear Credentials**: Remove stored credentials
- **Credential Info**: View stored credential information

Admin Page Configuration
~~~~~~~~~~~~~~~~~~~~~~~~

- **Custom Admin Page**: Optional custom admin page URL
- **Default**: Uses `http://127.0.0.1:8282/signin.html`

Settings Tab
------------

General Options
~~~~~~~~~~~~~~~

- **Auto-connect on startup**: Automatically connect when application starts
- **Minimize to system tray**: Hide window to system tray when minimized
- **Start with Windows**: Launch application when Windows starts
- **Debug mode**: Enable detailed logging and debugging features

Advanced Settings
~~~~~~~~~~~~~~~~~

- **Cleanup Old ChromeDrivers**: Remove outdated ChromeDriver files
- **ChromeDriver Management**: Automatic ChromeDriver download and management

System Integration
~~~~~~~~~~~~~~~~~~

- **Windows Startup**: Manages Windows startup registry entries
- **System Tray**: Provides system tray functionality with context menu

Logs Tab
--------

Real-time Logging
~~~~~~~~~~~~~~~~~

- **Live Log Display**: View application logs in real-time
- **Log Levels**: Filter logs by severity (INFO, WARNING, ERROR)
- **Auto-scroll**: Automatically scroll to latest log entries

Log Management
~~~~~~~~~~~~~~

- **Clear Logs**: Clear current log display
- **Save Logs**: Export logs to file
- **Log History**: View historical log information

System Tray
-----------

When "Minimize to system tray" is enabled:

- **Tray Icon**: Application icon appears in system tray
- **Context Menu**: Right-click for quick actions
  - Show: Restore application window
  - Connect: Start VPN connection
  - Disconnect: Stop VPN connection
  - Quit: Exit application
- **Notifications**: Tray notifications for status changes

Keyboard Shortcuts
------------------

- **Ctrl+Q**: Quit application
- **Ctrl+M**: Minimize to tray (if enabled)
- **F5**: Refresh status
- **Ctrl+L**: Focus log display

Troubleshooting
---------------

Common Issues
~~~~~~~~~~~~~

**Application won't start**
- Ensure you're running as Administrator
- Check that Python and dependencies are installed

**Connection fails**
- Verify Mudfish is installed and running
- Check credentials in the Credentials tab
- Review logs in the Logs tab

**Browser window appears**
- Uncheck "Show browser window" option
- This is normal when debugging is enabled

**System tray not working**
- Ensure "Minimize to system tray" is enabled in Settings
- Check Windows system tray settings

Getting Help
~~~~~~~~~~~~

1. Check the **Logs tab** for detailed error information
2. Review the **Status display** for connection details
3. Use **Debug mode** in Settings for verbose logging
4. Check the troubleshooting section in the main documentation
