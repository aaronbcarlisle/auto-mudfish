"""
Automated Mudfish VPN connection module.

This module provides the main automation functionality for starting Mudfish
VPN and establishing connections. It handles both process management and
web-based connection automation with fallback mechanisms.
"""

from typing import Optional
import sys
import logging
import argparse

from .process import MudfishProcess
from .connection import MudfishConnection

# Configure logging
logger = logging.getLogger("auto_mudfish.automate")


def auto_start(
    username: str,
    password: str,
    adminpage: Optional[str] = None,
    launcher: Optional[str] = None
) -> None:
    """
    Automatically start Mudfish VPN and establish a connection.
    
    This function orchestrates the complete Mudfish automation process:
    1. Ensures the Mudfish process is running
    2. Attempts headless login via HTTP requests
    3. Falls back to WebDriver-based login if needed
    4. Establishes the VPN connection
    
    Args:
        username (str): The username for the Mudfish account.
        password (str): The password for the Mudfish account.
        adminpage (Optional[str]): Custom admin page URL. If None, uses
                                 the default desktop admin page.
        launcher (Optional[str]): Custom path to the Mudfish launcher.
                                If None, auto-detects the launcher.
    
    Example:
        >>> auto_start("myuser", "mypassword")
        >>> auto_start("myuser", "mypassword", 
        ...            adminpage="http://192.168.1.1:8282/signin.html")
    """
    # Step 1: Ensure Mudfish process is running
    mudfish_process = MudfishProcess()
    mudfish_process_started = mudfish_process.start_mudfish_launcher(
        mudfish_launcher=launcher
    )
    logger.info("Mudfish process started: %s", mudfish_process_started)

    # Early return if Mudfish could not be started
    if not mudfish_process_started:
        logger.error("Mudfish is not running and could not be started. Aborting!")
        return

    # Step 2: Attempt headless login first (preferred method)
    mudfish_connection = MudfishConnection()
    
    if mudfish_connection.login_without_driver(username, password, adminpage=adminpage):
        logger.info("Logged in via headless method, proceeding to connect...")
        # Note: connect() method requires WebDriver, so we'll need to fall back
        # to WebDriver for the actual connection step
        logger.warning("Headless login successful, but connection requires WebDriver...")
    else:
        logger.warning("Headless login failed, falling back to WebDriver login...")

    # Step 3: Fallback to WebDriver-based login and connection
    from .driver import get_chrome_driver
    
    chrome_driver = get_chrome_driver()
    if not chrome_driver:
        logger.error("Chrome Driver is needed to continue, aborting!")
        return

    # Create connection with WebDriver for full automation
    mudfish_connection = MudfishConnection(web_driver=chrome_driver)
    mudfish_connection.login(username, password, adminpage=adminpage)
    mudfish_connection.connect()
    
    logger.info("Mudfish automation completed successfully!")


def main() -> None:
    """
    Main entry point for the command-line interface.
    
    Parses command-line arguments and executes the Mudfish automation process.
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
    default_adminpage = MudfishConnection.DEFAULT_DESKTOP_ADMIN_PAGE
    parser.add_argument(
        "-a", "--adminpage",
        default=default_adminpage,
        type=str,
        help=f"Admin page URL (default: {default_adminpage})"
    )
    parser.add_argument(
        "-l", "--launcher",
        type=str,
        help=f"Custom Mudfish launcher path (default: auto-detect)"
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
    
    # Execute automation
    try:
        auto_start(
            username=args.username,
            password=args.password,
            adminpage=args.adminpage,
            launcher=args.launcher
        )
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
    except Exception as e:
        logger.error("An error occurred during automation: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
