# Auto Mudfish VPN

A secure, automated solution for connecting to Mudfish VPN with encrypted credential storage and comprehensive automation features.

## Features

- **Secure Credential Storage** - Encrypted using Windows DPAPI
- **Full Automation** - One-click VPN connection
- **Multiple Connection Methods** - HTTP requests and WebDriver fallback
- **Process Management** - Automatic Mudfish launcher detection and startup
- **Security First** - No plain text passwords, user-specific encryption
- **Comprehensive Logging** - Detailed operation logs and error reporting
- **Full Test Coverage** - 38 unit tests ensuring reliability

## Quick Start

### Option 1: Download Executable (Recommended for Users)

**For users who just want to use the application:**

1. **Download the latest release** from the [releases page](https://github.com/aaronbcarlisle/auto-mudfish/tree/main/releases)
2. **Extract the files** from the version folder (e.g., `v1.0.1/`)
3. **Right-click `install.bat`** and select "Run as administrator"
4. **Follow the installation wizard** to install Auto Mudfish
5. **Launch from desktop shortcut** or Start Menu

**Note:** The installer requires administrator privileges to install the application and create shortcuts. After installation, you can run Auto Mudfish normally, but it will request administrator privileges when connecting to Mudfish.

The installer will:
- Install Auto Mudfish to `C:\Program Files\Auto Mudfish\`
- Create desktop and Start Menu shortcuts
- Set up the application for easy access

**Features:**
- **Easy credential setup** with secure storage
- **One-click VPN connection** 
- **Real-time status monitoring**
- **Detailed logs and troubleshooting**
- **Settings and preferences**

![Auto Mudfish VPN GUI](assets/gui-screenshot.png)
*The Auto Mudfish VPN GUI showing connection status and controls*

### Option 2: Python Development Setup

**For developers or users who prefer to run from source:**

```bash
# Install dependencies
pip install -r requirements.txt

# Launch GUI (requires administrator privileges)
python src/gui/gui.py

# OR use the provided PowerShell script to run as administrator
run_as_admin.ps1
```

**Important:** The GUI requires administrator privileges to launch Mudfish. You can either:
- Right-click the command prompt and select "Run as administrator", then run `python src/gui/gui.py`
- Use the provided `run_as_admin.ps1` file (PowerShell - recommended)
- For testing without elevation, use `run_gui.ps1` (but Mudfish connection will require admin privileges)

### Option 3: Command Line Interface

```bash
# Clone the repository
git clone https://github.com/aaronbcarlisle/auto-mudfish.git
cd auto-mudfish

# Install dependencies
pip install -r requirements.txt

# First time setup
python src/main.py --setup

# Connect to VPN
python src/main.py --use-stored
```

### Option 4: Unified Launcher

```bash
# Launch GUI
python src/launcher.py

# Launch CLI
python src/launcher.py --cli
```

## Usage

### Command Line Interface

```bash
python src/main.py [OPTIONS]
```

#### Credential Management
```bash
# Store credentials securely
python src/main.py --setup

# Use stored credentials
python src/main.py --use-stored

# View stored credential info (password hidden)
python src/main.py --show-credentials

# Clear stored credentials
python src/main.py --clear-credentials
```

#### Manual Authentication
```bash
# Use explicit credentials
python src/main.py -u username -p password

# With custom admin page
python src/main.py -u username -p password -a http://192.168.1.1:8282/signin.html

# With custom launcher path
python src/main.py -u username -p password -l "C:/Custom/Path/mudfish.exe"
```

#### Advanced Options
```bash
# Enable verbose logging
python src/main.py --use-stored -v

# Use stored credentials with custom admin page
python src/main.py --use-stored -a http://192.168.1.1:8282/signin.html

# Show browser window (for debugging)
python src/main.py --use-stored --show-browser
```

### GUI Application

The GUI provides an intuitive interface with four main tabs:

#### Main Tab
- **Connection Controls**: Connect, Disconnect, Check Status buttons
- **Status Display**: Real-time connection status and information
- **Options**: Show browser window, verbose logging

#### Credentials Tab
- **Credential Management**: Set up, view, and clear stored credentials
- **Secure Storage**: Credentials encrypted with Windows DPAPI
- **Admin Page Configuration**: Optional custom admin page URL

#### Settings Tab
- **General Options**: Auto-connect, minimize to tray, start with Windows
- **Advanced Settings**: Debug mode, ChromeDriver cleanup
- **System Integration**: Windows startup and system tray support

#### Logs Tab
- **Real-time Logging**: View application logs in real-time
- **Log Management**: Clear logs, save to file
- **Troubleshooting**: Detailed error information and debugging

### PowerShell Scripts

| Script | Purpose |
|--------|---------|
| `run_as_admin.ps1` | Launch GUI with administrator privileges |

### Complete Command Reference

```bash
usage: src/main.py [-h] [--setup] [--use-stored] [--show-credentials] [--clear-credentials] 
                   [-u USERNAME] [-p PASSWORD] [-a ADMINPAGE] [-l LAUNCHER] [-v]

Auto-connect Mudfish VPN

options:
  -h, --help            show this help message and exit
  --setup               Setup and store credentials securely
  --use-stored          Use stored credentials (no need to provide username/password)
  --show-credentials    Show stored credential information
  --clear-credentials   Clear stored credentials
  -u USERNAME, --username USERNAME
                        Username for the Mudfish account
  -p PASSWORD, --password PASSWORD
                        Password for the Mudfish account
  -a ADMINPAGE, --adminpage ADMINPAGE
                        Admin page URL (default: http://127.0.0.1:8282/signin.html)
  -l LAUNCHER, --launcher LAUNCHER
                        Custom Mudfish launcher path (default: auto-detect)
  -v, --verbose         Enable verbose logging
```

## Security

### Encryption & Storage
- **Windows DPAPI**: Credentials encrypted using your Windows user account
- **No Plain Text**: Passwords never stored in plain text or batch files
- **User-Specific**: Credentials cannot be decrypted by other users
- **Local Storage**: All data stored locally in `%USERPROFILE%\.auto_mudfish\`

### Best Practices
- Use `--setup` for initial credential storage
- Regularly clear credentials with `--clear-credentials` if needed
- Never share the `.auto_mudfish` folder
- Use `--show-credentials` to verify stored information

### Browser Behavior
- **Headless by Default**: Browser runs invisibly in the background
- **No Pop-ups**: No browser windows appear during normal operation
- **Debug Mode**: Use `--show-browser` to see browser window for troubleshooting
- **Automatic Cleanup**: Browser closes automatically after completion

## Architecture

The project follows a clean, organized structure:

```
auto-mudfish/
├── src/                    # Source code
│   ├── auto_mudfish/      # Core package
│   ├── gui/               # GUI application
│   ├── main.py            # CLI interface
│   └── launcher.py        # Unified launcher
├── scripts/               # Build and utility scripts
├── tests/                 # Test suite
├── docs/                  # Documentation
├── assets/                # Static assets
└── root entry points      # main.py, gui.py, launcher.py
```

### Core Components

| Module | Purpose |
|--------|---------|
| `src/auto_mudfish/credentials.py` | Secure credential encryption and storage |
| `src/auto_mudfish/connection.py` | Mudfish VPN connection management |
| `src/auto_mudfish/driver.py` | Chrome WebDriver automation |
| `src/auto_mudfish/process.py` | Mudfish process detection and management |
| `src/auto_mudfish/automate_mudfish.py` | High-level automation orchestration |
| `src/gui/gui.py` | PyQt6-based graphical user interface |

For detailed structure information, see [docs/STRUCTURE.md](docs/STRUCTURE.md).

### Connection Flow

1. **Process Check** - Verify Mudfish launcher is running
2. **Credential Loading** - Load from secure storage or user input
3. **HTTP Login** - Attempt headless login via HTTP requests
4. **WebDriver Fallback** - Use Chrome automation if HTTP fails
5. **VPN Connection** - Establish the VPN connection

## Testing

Run the complete test suite:

```bash
python -m unittest discover tests
```

The project includes 38 comprehensive unit tests covering:
- Credential encryption/decryption
- WebDriver management
- Connection logic
- Process detection
- Error handling

## Requirements

### System Requirements
- Windows 10/11
- Python 3.8+
- Chrome browser (for WebDriver fallback)

### Python Dependencies
- `selenium` - WebDriver automation
- `requests` - HTTP requests
- `beautifulsoup4` - HTML parsing
- `psutil` - Process management
- `pywin32` - Windows API access
- `get-chrome-driver` - Automatic ChromeDriver management

## Development

### Project Structure
```
auto-mudfish/
├── src/                   # Source code
│   ├── auto_mudfish/     # Main package
│   │   ├── credentials.py # Secure credential management
│   │   ├── connection.py  # VPN connection logic
│   │   ├── driver.py      # WebDriver management
│   │   ├── process.py     # Process management
│   │   └── automate_mudfish.py # Automation orchestration
│   ├── gui/              # GUI application
│   │   └── gui.py        # PyQt6 GUI
│   ├── main.py           # CLI entry point
│   └── launcher.py       # Unified launcher
├── tests/                # Unit tests
├── scripts/              # Build and utility scripts
├── assets/               # Static assets (icons, etc.)
├── docs/                 # Documentation
└── requirements.txt      # Dependencies
```

### Adding Features
1. Add functionality to appropriate module
2. Write comprehensive unit tests
3. Update documentation
4. Test with both stored and explicit credentials

## Troubleshooting

### Common Issues

**"No stored credentials found"**
```bash
# Run setup to store credentials
python src/main.py --setup
```

**"Chrome Driver not found"**
```bash
# The app will auto-download ChromeDriver, but ensure Chrome is installed
```

**"Mudfish not running"**
```bash
# Ensure Mudfish is installed and the launcher is accessible
# Check the default path: C:/Program Files (x86)/Mudfish Cloud VPN/mudrun.exe
```

**"Failed to decrypt credentials"**
```bash
# Clear and re-setup credentials
python src/main.py --clear-credentials
python src/main.py --setup
```

### Debug Mode
Enable verbose logging for detailed troubleshooting:

```bash
python src/main.py --use-stored -v
```

## License

This project is open source. Please ensure you comply with Mudfish's terms of service when using this automation tool.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the test suite for usage examples
3. Open an issue on GitHub

---

**Note**: This tool is designed for personal use with your own Mudfish account. Always ensure you comply with Mudfish's terms of service and applicable laws in your jurisdiction.