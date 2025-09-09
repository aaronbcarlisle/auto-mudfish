#!/usr/bin/env python3
"""
Auto Mudfish VPN - Launcher Entry Point

This is the unified launcher for the Auto Mudfish VPN application.
It can launch either the GUI or CLI based on command line arguments.
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

if __name__ == "__main__":
    # Import and run the launcher
    from src.launcher import main
    main()
