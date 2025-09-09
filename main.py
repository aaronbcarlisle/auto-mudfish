#!/usr/bin/env python3
"""
Main entry point for the auto-mudfish application.

This script provides a command-line interface for automatically starting
Mudfish VPN and establishing connections. It serves as the primary entry
point for the application and handles command-line argument parsing.
"""

import sys
import logging
import argparse
from typing import Optional

from auto_mudfish.connection import MudfishConnection
from auto_mudfish.driver import get_chrome_driver
from auto_mudfish.process import MudfishProcess

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("auto_mudfish.main")


def main(
    username: str,
    password: str,
    adminpage: Optional[str] = None,
    launcher: Optional[str] = None
) -> None:
    """
    Main function that orchestrates Mudfish VPN automation.
    
    This function handles the complete automation workflow:
    1. Ensures Mudfish process is running
    2. Attempts headless login via HTTP requests
    3. Falls back to WebDriver-based automation if needed
    4. Establishes the VPN connection
    
    Args:
        username (str): The username for the Mudfish account.
        password (str): The password for the Mudfish account.
        adminpage (Optional[str]): Custom admin page URL. If None, uses
                                 the default desktop admin page.
        launcher (Optional[str]): Custom path to the Mudfish launcher.
                                If None, auto-detects the launcher.
    
    Raises:
        SystemExit: If Mudfish cannot be started or critical errors occur.
    """
    logger.info("Starting Mudfish automation process...")
    
    # Step 1: Ensure Mudfish process is running
    mudfish_process = MudfishProcess()
    if not mudfish_process.start_mudfish_launcher(mudfish_launcher=launcher):
        logger.error("Mudfish is not running and could not be started. Aborting!")
        sys.exit(1)

    # Step 2: Attempt headless login first (preferred method)
    mudfish_connection = MudfishConnection(web_driver=None)
    if mudfish_connection.login_without_driver(
        username=username,
        password=password,
        adminpage=adminpage
    ):
        logger.info("Logged in via headless method, proceeding to connect...")
        # Note: connect() requires WebDriver, so we need to fall back for connection
        logger.warning("Headless login successful, but connection requires WebDriver...")
    else:
        logger.warning("Headless login failed, falling back to WebDriver login...")

    # Step 3: Fallback to WebDriver-based login and connection
    chrome_driver = get_chrome_driver()
    if not chrome_driver:
        logger.error("Chrome Driver is needed to continue, aborting!")
        sys.exit(1)

    # Re-initialize MudfishConnection with the ChromeDriver
    mudfish_connection = MudfishConnection(web_driver=chrome_driver)
    mudfish_connection.login(username=username, password=password, adminpage=adminpage)
    mudfish_connection.connect()

    logger.info("Mudfish login and connection process completed successfully!")

def cli() -> None:
    """
    Command-line interface for the auto-mudfish application.
    
    Parses command-line arguments and executes the main automation function.
    """
    # Setup argument parser
    parser = argparse.ArgumentParser(
        description="Auto-connect Mudfish VPN",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s -u myuser -p mypassword
  %(prog)s -u myuser -p mypassword -a http://192.168.1.1:8282/signin.html
  %(prog)s -u myuser -p mypassword -l "C:/Custom/Path/mudfish.exe"
  %(prog)s -u myuser -p mypassword -v
        """
    )

    # Required arguments
    parser.add_argument(
        "-u", "--username",
        type=str,
        required=True,
        help="Username for the Mudfish account"
    )
    parser.add_argument(
        "-p", "--password",
        type=str,
        required=True,
        help="Password for the Mudfish account"
    )

    # Optional arguments
    parser.add_argument(
        "-a", "--adminpage",
        default=MudfishConnection.DEFAULT_DESKTOP_ADMIN_PAGE,
        type=str,
        help=f"Admin page URL (default: {MudfishConnection.DEFAULT_DESKTOP_ADMIN_PAGE})"
    )
    parser.add_argument(
        "-l", "--launcher",
        type=str,
        help="Custom Mudfish launcher path (default: auto-detect)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )

    # Parse arguments
    args = parser.parse_args()
    
    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Log parsed arguments (excluding password for security)
    main_kwargs = vars(args).copy()
    main_kwargs['password'] = '***'  # Hide password in logs
    logger.debug("Parsed arguments: %s", main_kwargs)
    
    # Execute main function
    try:
        main(
            username=args.username,
            password=args.password,
            adminpage=args.adminpage,
            launcher=args.launcher
        )
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        sys.exit(0)
    except Exception as e:
        logger.error("An unexpected error occurred: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    cli()
