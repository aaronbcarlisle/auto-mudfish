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
import getpass
from typing import Optional

from auto_mudfish.connection import MudfishConnection
from auto_mudfish.driver import get_chrome_driver
from auto_mudfish.process import MudfishProcess
from auto_mudfish.credentials import get_credential_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("auto_mudfish.main")


def setup_credentials() -> bool:
    """
    Interactive setup for storing credentials.
    
    Returns:
        bool: True if credentials were stored successfully.
    """
    print("\n=== Mudfish Credential Setup ===")
    print("This will securely store your Mudfish credentials for future use.")
    print("Credentials are encrypted using Windows DPAPI and stored locally.\n")
    
    try:
        # Get username
        username = input("Enter your Mudfish username: ").strip()
        if not username:
            print("Username cannot be empty!")
            return False
        
        # Get password (hidden input)
        password = getpass.getpass("Enter your Mudfish password: ")
        if not password:
            print("Password cannot be empty!")
            return False
        
        # Get admin page (optional)
        adminpage = input("Enter admin page URL (optional, press Enter for default): ").strip()
        if not adminpage:
            adminpage = None
        
        # Store credentials
        cred_manager = get_credential_manager()
        if cred_manager.store_credentials(username, password, adminpage):
            print("✅ Credentials stored successfully!")
            return True
        else:
            print("❌ Failed to store credentials!")
            return False
            
    except KeyboardInterrupt:
        print("\nSetup cancelled by user.")
        return False
    except Exception as e:
        print(f"❌ Error during setup: {e}")
        return False


def clear_credentials() -> bool:
    """
    Clear stored credentials.
    
    Returns:
        bool: True if credentials were cleared successfully.
    """
    try:
        cred_manager = get_credential_manager()
        if cred_manager.clear_credentials():
            print("✅ Credentials cleared successfully!")
            return True
        else:
            print("❌ Failed to clear credentials!")
            return False
    except Exception as e:
        print(f"❌ Error clearing credentials: {e}")
        return False


def show_credentials() -> None:
    """Show stored credential information (without password)."""
    try:
        cred_manager = get_credential_manager()
        if not cred_manager.has_credentials():
            print("No credentials stored.")
            return
        
        info = cred_manager.get_credentials_info()
        if info:
            print("\n=== Stored Credentials ===")
            print(f"Username: {info['username']}")
            print(f"Admin Page: {info['adminpage'] or 'Default'}")
            print(f"Password: {'***' if info['has_password'] else 'Not set'}")
        else:
            print("Failed to load credential information.")
    except Exception as e:
        print(f"❌ Error showing credentials: {e}")


def load_credentials() -> Optional[tuple[str, str, Optional[str]]]:
    """
    Load stored credentials.
    
    Returns:
        Optional[tuple[str, str, Optional[str]]]: (username, password, adminpage) or None.
    """
    try:
        cred_manager = get_credential_manager()
        credentials = cred_manager.load_credentials()
        
        if credentials:
            username = credentials.get("username", "")
            password = credentials.get("password", "")
            adminpage = credentials.get("adminpage")
            
            if username and password:
                logger.info("Loaded credentials from secure storage")
                return username, password, adminpage
            else:
                logger.warning("Incomplete credentials in storage")
                return None
        else:
            logger.debug("No credentials found in storage")
            return None
            
    except Exception as e:
        logger.error("Failed to load credentials: %s", e)
        return None


def main(
    username: Optional[str] = None,
    password: Optional[str] = None,
    adminpage: Optional[str] = None,
    launcher: Optional[str] = None,
    use_stored: bool = False,
    show_browser: bool = False
) -> None:
    """
    Main function that orchestrates Mudfish VPN automation.
    
    This function handles the complete automation workflow:
    1. Ensures Mudfish process is running
    2. Attempts headless login via HTTP requests
    3. Falls back to WebDriver-based automation if needed
    4. Establishes the VPN connection
    
    Args:
        username (Optional[str]): The username for the Mudfish account.
                                 If None and use_stored=True, loads from storage.
        password (Optional[str]): The password for the Mudfish account.
                                 If None and use_stored=True, loads from storage.
        adminpage (Optional[str]): Custom admin page URL. If None, uses
                                 the default desktop admin page or stored value.
        launcher (Optional[str]): Custom path to the Mudfish launcher.
                                If None, auto-detects the launcher.
        use_stored (bool): If True, attempt to load credentials from secure storage.
        show_browser (bool): If True, show browser window (for debugging).
    
    Raises:
        SystemExit: If Mudfish cannot be started or critical errors occur.
    """
    logger.info("Starting Mudfish automation process...")
    
    # Load credentials if requested
    if use_stored or (username is None and password is None):
        stored_creds = load_credentials()
        if stored_creds:
            stored_username, stored_password, stored_adminpage = stored_creds
            if username is None:
                username = stored_username
            if password is None:
                password = stored_password
            if adminpage is None and stored_adminpage:
                adminpage = stored_adminpage
        else:
            logger.error("No stored credentials found and no credentials provided!")
            logger.info("Run 'python main.py --setup' to store credentials securely.")
            sys.exit(1)
    
    # Validate required credentials
    if not username or not password:
        logger.error("Username and password are required!")
        logger.info("Run 'python main.py --setup' to store credentials securely.")
        sys.exit(1)
    
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
    chrome_driver = get_chrome_driver(headless=not show_browser)
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
  %(prog)s --setup                    # Store credentials securely
  %(prog)s --use-stored               # Use stored credentials
  %(prog)s --use-stored --show-browser # Use stored credentials with visible browser
  %(prog)s --show-credentials         # Show stored credential info
  %(prog)s --clear-credentials        # Clear stored credentials
  %(prog)s --cleanup-chromedriver     # Clean up old ChromeDriver versions
        """
    )

    # Credential management commands
    parser.add_argument(
        "--setup",
        action="store_true",
        help="Setup and store credentials securely"
    )
    parser.add_argument(
        "--use-stored",
        action="store_true",
        help="Use stored credentials (no need to provide username/password)"
    )
    parser.add_argument(
        "--show-credentials",
        action="store_true",
        help="Show stored credential information"
    )
    parser.add_argument(
        "--clear-credentials",
        action="store_true",
        help="Clear stored credentials"
    )

    # Authentication arguments
    parser.add_argument(
        "-u", "--username",
        type=str,
        help="Username for the Mudfish account"
    )
    parser.add_argument(
        "-p", "--password",
        type=str,
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
    parser.add_argument(
        "--show-browser",
        action="store_true",
        help="Show browser window (for debugging)"
    )
    parser.add_argument(
        "--cleanup-chromedriver",
        action="store_true",
        help="Clean up old ChromeDriver versions"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode with detailed logging"
    )

    # Parse arguments
    args = parser.parse_args()
    
    # Configure logging level
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    elif args.verbose:
        logging.getLogger().setLevel(logging.INFO)
    else:
        logging.getLogger().setLevel(logging.WARNING)
    
    # Handle credential management commands
    if args.setup:
        success = setup_credentials()
        sys.exit(0 if success else 1)
    
    if args.show_credentials:
        show_credentials()
        sys.exit(0)
    
    if args.clear_credentials:
        success = clear_credentials()
        sys.exit(0 if success else 1)
    
    if args.cleanup_chromedriver:
        from auto_mudfish.driver import _cleanup_old_chromedrivers
        _cleanup_old_chromedrivers()
        print("✅ ChromeDriver cleanup completed!")
        sys.exit(0)
    
    # Validate arguments for main function
    if not args.use_stored and (not args.username or not args.password):
        parser.error("Username and password are required unless using --use-stored")
    
    # Log parsed arguments (excluding password for security)
    main_kwargs = vars(args).copy()
    if main_kwargs.get('password'):
        main_kwargs['password'] = '***'  # Hide password in logs
    logger.debug("Parsed arguments: %s", main_kwargs)
    
    # Execute main function
    try:
        main(
            username=args.username,
            password=args.password,
            adminpage=args.adminpage,
            launcher=args.launcher,
            use_stored=args.use_stored,
            show_browser=args.show_browser
        )
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        sys.exit(0)
    except Exception as e:
        logger.error("An unexpected error occurred: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    cli()
