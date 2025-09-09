"""
Chrome WebDriver management module for auto-mudfish.

This module provides functionality to create and manage Chrome WebDriver instances
with automatic driver downloading and configuration for headless operation.
"""

from typing import Optional
import os
import logging
import requests
import zipfile
import tempfile

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.common.exceptions import SessionNotCreatedException

from get_chrome_driver import GetChromeDriver
from get_chrome_driver.enums.os_platform import OsPlatform

# Configure logging
logger = logging.getLogger("auto_mudfish.driver")


def _cleanup_old_chromedrivers():
    """Clean up old ChromeDriver versions to save space."""
    try:
        home_dir = os.path.expanduser("~")
        chromedriver_dir = os.path.join(home_dir, ".auto_mudfish", "chromedriver")
        
        if not os.path.exists(chromedriver_dir):
            return
        
        # Get all version directories
        version_dirs = [d for d in os.listdir(chromedriver_dir) 
                       if os.path.isdir(os.path.join(chromedriver_dir, d))]
        
        if len(version_dirs) <= 3:  # Keep last 3 versions
            return
        
        # Sort by version and remove oldest
        version_dirs.sort(reverse=True)
        for old_version in version_dirs[3:]:
            old_dir = os.path.join(chromedriver_dir, old_version)
            try:
                import shutil
                shutil.rmtree(old_dir)
                logger.debug("Cleaned up old ChromeDriver version: %s", old_version)
            except Exception as e:
                logger.debug("Failed to clean up old ChromeDriver %s: %s", old_version, e)
                
    except Exception as e:
        logger.debug("Failed to clean up old ChromeDrivers: %s", e)


def _download_specific_chromedriver(headless: bool = True) -> Optional[webdriver.Chrome]:
    """
    Download a specific ChromeDriver version that matches the installed Chrome version.
    
    Args:
        headless (bool): Whether to run Chrome in headless mode.
        
    Returns:
        Optional[webdriver.Chrome]: ChromeDriver instance if successful, None otherwise.
    """
    try:
        # Get Chrome version
        import subprocess
        result = subprocess.run([
            "reg", "query", 
            "HKEY_CURRENT_USER\\Software\\Google\\Chrome\\BLBeacon", 
            "/v", "version"
        ], capture_output=True, text=True, shell=True)
        
        if result.returncode != 0:
            # Try alternative registry path
            result = subprocess.run([
                "reg", "query", 
                "HKEY_LOCAL_MACHINE\\SOFTWARE\\Google\\Chrome\\BLBeacon", 
                "/v", "version"
            ], capture_output=True, text=True, shell=True)
        
        if result.returncode != 0:
            logger.error("Could not determine Chrome version")
            return None
            
        # Extract version number
        version_line = [line for line in result.stdout.split('\n') if 'version' in line.lower()]
        if not version_line:
            logger.error("Could not parse Chrome version")
            return None
            
        chrome_version = version_line[0].split()[-1]
        major_version = chrome_version.split('.')[0]
        
        logger.info("Detected Chrome version: %s (major: %s)", chrome_version, major_version)
        
        # Try multiple approaches to get ChromeDriver
        download_url = None
        driver_version = None
        
        # Approach 1: Try Chrome for Testing API (newest)
        try:
            api_url = f"https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_{major_version}"
            response = requests.get(api_url, timeout=10)
            if response.status_code == 200:
                driver_version = response.text.strip()
                logger.info("Found ChromeDriver version (Chrome for Testing): %s", driver_version)
                download_url = f"https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/{driver_version}/win32/chromedriver-win32.zip"
        except Exception as e:
            logger.debug("Chrome for Testing API failed: %s", e)
        
        # Approach 2: Try old Google Storage API
        if not download_url:
            try:
                chromedriver_url = f"https://chromedriver.storage.googleapis.com/LATEST_RELEASE_{major_version}"
                response = requests.get(chromedriver_url, timeout=10)
                if response.status_code == 200:
                    driver_version = response.text.strip()
                    logger.info("Found ChromeDriver version (Google Storage): %s", driver_version)
                    download_url = f"https://chromedriver.storage.googleapis.com/{driver_version}/chromedriver_win32.zip"
            except Exception as e:
                logger.debug("Google Storage API failed: %s", e)
        
        # Approach 3: Try direct version matching
        if not download_url:
            try:
                # Try to find a compatible version by testing a few common ones
                test_versions = [
                    f"{major_version}.0.0.0",
                    f"{major_version}.0.6778.85",  # Common stable version
                    f"{major_version}.0.6998.165", # Another common version
                ]
                
                for test_version in test_versions:
                    test_url = f"https://chromedriver.storage.googleapis.com/{test_version}/chromedriver_win32.zip"
                    try:
                        response = requests.head(test_url, timeout=5)
                        if response.status_code == 200:
                            driver_version = test_version
                            download_url = test_url
                            logger.info("Found compatible ChromeDriver version: %s", driver_version)
                            break
                    except:
                        continue
            except Exception as e:
                logger.debug("Direct version matching failed: %s", e)
        
        # Approach 4: Last resort - use major version
        if not download_url:
            driver_version = major_version
            download_url = f"https://chromedriver.storage.googleapis.com/{driver_version}/chromedriver_win32.zip"
            logger.warning("Using major version as fallback: %s", driver_version)
        
        # Create a permanent directory for ChromeDriver in user's home directory
        home_dir = os.path.expanduser("~")
        chromedriver_dir = os.path.join(home_dir, ".auto_mudfish", "chromedriver")
        os.makedirs(chromedriver_dir, exist_ok=True)
        
        # Create a versioned subdirectory
        version_dir = os.path.join(chromedriver_dir, driver_version)
        os.makedirs(version_dir, exist_ok=True)
        
        chromedriver_exe = os.path.join(version_dir, "chromedriver.exe")
        
        # Check if we already have this version
        if os.path.exists(chromedriver_exe):
            logger.info("Using existing ChromeDriver: %s", chromedriver_exe)
            return ChromeDriver(headless=headless, executable_path=chromedriver_exe)
        
        # Download and extract to permanent location
        with tempfile.TemporaryDirectory() as temp_dir:
            logger.info("Downloading ChromeDriver from: %s", download_url)
            response = requests.get(download_url, timeout=30)
            response.raise_for_status()
            
            # Save and extract
            zip_path = os.path.join(temp_dir, "chromedriver.zip")
            with open(zip_path, 'wb') as f:
                f.write(response.content)
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # Find chromedriver.exe (handle both old and new formats)
            chromedriver_path = None
            for root, dirs, files in os.walk(temp_dir):
                if 'chromedriver.exe' in files:
                    chromedriver_path = os.path.join(root, 'chromedriver.exe')
                    break
            
            if not chromedriver_path:
                # Try to find it in subdirectories (new Chrome for Testing format)
                for root, dirs, files in os.walk(temp_dir):
                    for subdir in dirs:
                        subdir_path = os.path.join(root, subdir)
                        for subroot, subdirs, subfiles in os.walk(subdir_path):
                            if 'chromedriver.exe' in subfiles:
                                chromedriver_path = os.path.join(subroot, 'chromedriver.exe')
                                break
                        if chromedriver_path:
                            break
                    if chromedriver_path:
                        break
            
            if not chromedriver_path:
                logger.error("Could not find chromedriver.exe in downloaded archive")
                return None
            
            # Copy to permanent location
            import shutil
            try:
                shutil.copy2(chromedriver_path, chromedriver_exe)
                logger.info("ChromeDriver saved to: %s", chromedriver_exe)
            except Exception as e:
                logger.error("Failed to copy ChromeDriver to permanent location: %s", e)
                return None
            
            # Create ChromeDriver instance
            driver = ChromeDriver(headless=headless, executable_path=chromedriver_exe)
            
            # Clean up old versions
            _cleanup_old_chromedrivers()
            
            return driver
            
    except Exception as e:
        logger.error("Failed to download specific ChromeDriver version: %s", e)
        return None


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
            logger.info("Attempting to download specific ChromeDriver version...")
            
            # Second fallback: Try to download a specific version
            try:
                return _download_specific_chromedriver(headless)
            except Exception as download_error:
                logger.error("Failed to download specific ChromeDriver version: %s", download_error)
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
            chrome_options.add_argument("--headless=new")  # Use new headless mode
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--disable-features=VizDisplayCompositor")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-plugins")
            chrome_options.add_argument("--disable-images")
            # Note: We need JavaScript for Mudfish interface, so don't disable it
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

