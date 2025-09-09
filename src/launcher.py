#!/usr/bin/env python3
"""
Launcher script for Auto Mudfish.

This script can launch either the GUI application or the command-line interface
based on the arguments provided.
"""

import sys
import os
import argparse

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    """Main launcher function."""
    parser = argparse.ArgumentParser(
        description="Auto Mudfish VPN Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python launcher.py                    # Launch GUI
  python launcher.py --cli --help      # Show CLI help
  python launcher.py --cli --setup     # Run CLI setup
  python launcher.py --cli --use-stored # Run CLI with stored credentials
        """
    )
    
    parser.add_argument(
        "--cli",
        action="store_true",
        help="Launch command-line interface instead of GUI"
    )
    
    # Parse known args to separate launcher args from CLI args
    args, remaining_args = parser.parse_known_args()
    
    if args.cli:
        # Launch CLI version
        from main import cli
        # Replace sys.argv with remaining args for CLI
        sys.argv = ['main.py'] + remaining_args
        cli()
    else:
        # Launch GUI version
        try:
            from gui import main as gui_main
            gui_main()
        except ImportError as e:
            print(f"Error launching GUI: {e}")
            print("Make sure PyQt6 is installed: pip install PyQt6")
            print("Falling back to CLI...")
            from main import cli
            cli()


if __name__ == "__main__":
    main()
