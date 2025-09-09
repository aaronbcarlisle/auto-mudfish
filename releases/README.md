# Auto Mudfish VPN Releases

This directory contains organized release packages for Auto Mudfish VPN.

## Structure

```
releases/
├── v1.0.0/           # Version 1.0.0 release
│   ├── AutoMudfish.exe
│   ├── install.bat
│   ├── README_EXECUTABLE.txt
│   └── RELEASE_NOTES_v1.0.0.md
├── v1.0.1/           # Version 1.0.1 release
│   └── ...
└── README.md         # This file
```

## How to Use

1. **Download**: Navigate to the version folder you want (e.g., `v1.0.1/`)
2. **Install**: Run `install.bat` as Administrator
3. **Read**: Check `RELEASE_NOTES_vX.X.X.md` for version-specific information

## Building New Releases

To create a new release:

```bash
# Build with specific version
python scripts/build_exe.py 1.0.2

# Or build with default version
python scripts/build_exe.py
```

The build script will automatically:
- Create the executable
- Generate installer and documentation
- Organize files into `releases/vX.X.X/` folder
- Create release notes

## GitHub Actions

Releases are automatically built when:
- A new tag is pushed (e.g., `git tag v1.0.2 && git push origin v1.0.2`)
- The workflow is manually triggered with a version number

## File Descriptions

- **AutoMudfish.exe**: The main application executable
- **install.bat**: Windows installer script (requires admin privileges)
- **README_EXECUTABLE.txt**: User documentation for the executable
- **RELEASE_NOTES_vX.X.X.md**: Version-specific release notes and changelog
