"""
Chrome WebDriver management module for auto-mudfish.

This module provides functionality to create and manage Chrome WebDriver instances
with automatic driver downloading and configuration for headless operation.
"""

from typing import Optional
import os
import logging

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.common.exceptions import SessionNotCreatedException

from get_chrome_driver import GetChromeDriver
from get_chrome_driver.enums.os_platform import OsPlatform

# Configure logging
logger = logging.getLogger("auto_mudfish.driver")


def get_chrome_driver(headless: bool = True) -> Optional[webdriver.Chrome]:
    """
    Create and configure a Chrome WebDriver instance with automatic driver management.
    
    This function automatically downloads the appropriate ChromeDriver for the current
    Chrome version and creates a configured ChromeDriver instance. It handles driver
    installation and extraction automatically.
    
    Args:
        headless (bool, optional): Whether to run Chrome in headless mode. 
                                  Defaults to True for automated operation.
    
    Returns:
        Optional[webdriver.Chrome]: A configured ChromeDriver instance if successful,
                                   None if driver creation fails.
    
    Example:
        >>> driver = get_chrome_driver(headless=True)
        >>> if driver:
        ...     driver.get("https://example.com")
        ...     driver.quit()
    """
    try:
        # Download and extract the appropriate ChromeDriver
        chrome_driver_installer = GetChromeDriver(os_platform=OsPlatform.win)
        output_path = chrome_driver_installer.auto_download(extract=True)
        
        # Create ChromeDriver with the downloaded executable
        executable_path = os.path.join(output_path, "chromedriver.exe")
        return ChromeDriver(headless=headless, executable_path=executable_path)
        
    except Exception as e:
        logger.warning("Failed to download ChromeDriver: %s", e)
        logger.info("Attempting to use system ChromeDriver...")
        
        # Fallback: Try to use system ChromeDriver
        try:
            return ChromeDriver(headless=headless)
        except Exception as fallback_error:
            logger.error("Failed to create Chrome WebDriver with system driver: %s", fallback_error)
            logger.error("Please ensure Chrome browser is installed and up to date")
            return None


class ChromeDriver(webdriver.Chrome):
    """
    Extended Chrome WebDriver with enhanced configuration options.
    
    This class extends the standard Selenium Chrome WebDriver to provide
    additional configuration options and simplified setup for automated
    browser operations.
    
    Attributes:
        options: The ChromeOptions instance used for browser configuration.
    """
    
    def __init__(
        self,
        options: Optional[Options] = None,
        service: Optional[Service] = None,
        keep_alive: bool = True,
        headless: bool = False,
        executable_path: Optional[str] = None
    ) -> None:
        """
        Initialize a new ChromeDriver instance with enhanced configuration.
        
        Args:
            options (Optional[Options]): ChromeOptions instance for browser configuration.
                                        If None, default options will be used.
            service (Optional[Service]): Service object for handling the browser driver.
                                        If None, a default service will be created.
            keep_alive (bool, optional): Whether to configure ChromeRemoteConnection 
                                       to use HTTP keep-alive. Defaults to True.
            headless (bool, optional): Whether to run Chrome in headless mode.
                                     Defaults to False.
            executable_path (Optional[str]): Path to the ChromeDriver executable.
                                           If provided, will be used instead of system PATH.
        
        Raises:
            SessionNotCreatedException: If the WebDriver session cannot be created.
            WebDriverException: If there's an error initializing the WebDriver.
        
        Example:
            >>> # Create a headless driver
            >>> driver = ChromeDriver(headless=True)
            >>> 
            >>> # Create a driver with custom options
            >>> options = webdriver.ChromeOptions()
            >>> options.add_argument("--disable-images")
            >>> driver = ChromeDriver(options=options, headless=True)
        """
        # Store options for potential future use
        self.options = options
        
        # Configure headless mode if requested
        if headless:
            chrome_options = self.options or webdriver.ChromeOptions()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            self.options = chrome_options
        
        # Create service with executable path if provided
        if executable_path:
            service = Service(executable_path=executable_path)
        elif service is None:
            service = Service()
        
        # Initialize the parent Chrome WebDriver
        super().__init__(
            options=self.options,
            service=service,
            keep_alive=keep_alive
        )

