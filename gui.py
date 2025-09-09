#!/usr/bin/env python3
"""
Auto Mudfish VPN - GUI Entry Point

This is the GUI entry point for the Auto Mudfish VPN application.
It launches the PyQt6-based graphical user interface.
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

if __name__ == "__main__":
    # Import and run the GUI
    from src.gui import main
    main()
