#!/usr/bin/env python3
"""
Auto Mudfish VPN - Main Entry Point

This is the main entry point for the Auto Mudfish VPN application.
It redirects to the appropriate module based on the command line arguments.
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

if __name__ == "__main__":
    # Import and run the main CLI
    from src.main import cli
    cli()
