# Auto Mudfish VPN

A secure, automated solution for connecting to Mudfish VPN with encrypted credential storage and comprehensive automation features.

## ✨ Features

- **🔐 Secure Credential Storage** - Encrypted using Windows DPAPI
- **🤖 Full Automation** - One-click VPN connection
- **🌐 Multiple Connection Methods** - HTTP requests and WebDriver fallback
- **📱 Process Management** - Automatic Mudfish launcher detection and startup
- **🛡️ Security First** - No plain text passwords, user-specific encryption
- **📊 Comprehensive Logging** - Detailed operation logs and error reporting
- **🧪 Full Test Coverage** - 38 unit tests ensuring reliability

## 🚀 Quick Start

### Option 1: GUI Application (Recommended)

```bash
# Install dependencies
pip install -r requirements.txt

# Launch GUI
python gui.py
```

The GUI provides:
- **Easy credential setup** with secure storage
- **One-click VPN connection** 
- **Real-time status monitoring**
- **Detailed logs and troubleshooting**
- **Settings and preferences**

### Option 2: Command Line Interface

```bash
# Clone the repository
git clone https://github.com/aaronbcarlisle/auto-mudfish.git
cd auto-mudfish

# Install dependencies
pip install -r requirements.txt

# First time setup
python main.py --setup

# Connect to VPN
python main.py --use-stored
```

### Option 3: Executable Distribution

For users without Python:

```bash
# Build executable
scripts\build.bat

# Or manually
python scripts\build_exe.py
```

This creates a standalone executable that can be distributed without requiring Python installation.

### Option 4: Installer Package

For easy distribution and installation:

```bash
# Build installer
scripts\build_installer.bat

# Or manually
python scripts\build_installer.py
```

This creates a professional installer package with:
- **Graphical Installer**: PyQt6-based installation wizard
- **Simple Installer**: Automated batch script installer
- **Complete Package**: Ready for distribution

The installer package includes:
- Step-by-step installation wizard
- Customizable installation options
- Automatic shortcut creation
- Uninstaller generation
- System integration

### Option 5: Unified Launcher

```bash
# Launch GUI
python launcher.py

# Launch CLI
python launcher.py --cli
```

## 📖 Usage

### Command Line Interface

```bash
python main.py [OPTIONS]
```

#### Credential Management
```bash
# Store credentials securely
python main.py --setup

# Use stored credentials
python main.py --use-stored

# View stored credential info (password hidden)
python main.py --show-credentials

# Clear stored credentials
python main.py --clear-credentials
```

#### Manual Authentication
```bash
# Use explicit credentials
python main.py -u username -p password

# With custom admin page
python main.py -u username -p password -a http://192.168.1.1:8282/signin.html

# With custom launcher path
python main.py -u username -p password -l "C:/Custom/Path/mudfish.exe"
```

#### Advanced Options
```bash
# Enable verbose logging
python main.py --use-stored -v

# Use stored credentials with custom admin page
python main.py --use-stored -a http://192.168.1.1:8282/signin.html

# Show browser window (for debugging)
python main.py --use-stored --show-browser
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

### Batch Scripts

| Script | Purpose |
|--------|---------|
| `start_mudfish.bat` | Connect using stored credentials (recommended) |
| `setup_credentials.bat` | Interactive credential setup |

### Complete Command Reference

```bash
usage: main.py [-h] [--setup] [--use-stored] [--show-credentials] [--clear-credentials] 
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

## 🔒 Security

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

## 🏗️ Architecture

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

## 🧪 Testing

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

## 📋 Requirements

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

## 🛠️ Development

### Project Structure
```
auto-mudfish/
├── auto_mudfish/           # Main package
│   ├── credentials.py     # Secure credential management
│   ├── connection.py      # VPN connection logic
│   ├── driver.py          # WebDriver management
│   ├── process.py         # Process management
│   └── automate_mudfish.py # Automation orchestration
├── tests/                 # Unit tests
├── main.py               # CLI entry point
├── start_mudfish.bat     # Convenience batch file
└── requirements.txt      # Dependencies
```

### Adding Features
1. Add functionality to appropriate module
2. Write comprehensive unit tests
3. Update documentation
4. Test with both stored and explicit credentials

## 🐛 Troubleshooting

### Common Issues

**"No stored credentials found"**
```bash
# Run setup to store credentials
python main.py --setup
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
python main.py --clear-credentials
python main.py --setup
```

### Debug Mode
Enable verbose logging for detailed troubleshooting:

```bash
python main.py --use-stored -v
```

## 📝 License

This project is open source. Please ensure you comply with Mudfish's terms of service when using this automation tool.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the test suite for usage examples
3. Open an issue on GitHub

---

**Note**: This tool is designed for personal use with your own Mudfish account. Always ensure you comply with Mudfish's terms of service and applicable laws in your jurisdiction.