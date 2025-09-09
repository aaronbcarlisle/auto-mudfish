"""
Mudfish VPN connection management module.

This module provides functionality to interact with Mudfish VPN through both
Selenium WebDriver automation and direct HTTP requests for login and connection
management.
"""

from typing import Optional
import logging

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
import requests
from bs4 import BeautifulSoup
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException

from .driver import ChromeDriver

# Configure logging
logger = logging.getLogger("auto_mudfish.connection")


class MudfishConnection:
    """
    Manages Mudfish VPN connections through web automation.
    
    This class provides methods to login to Mudfish VPN and control the
    connection state (connect/disconnect) using either Selenium WebDriver
    automation or direct HTTP requests.
    
    Attributes:
        STOP_BUTTON_ID: Tuple containing the locator for the disconnect button.
        START_BUTTON_ID: Tuple containing the locator for the connect button.
        DEFAULT_DESKTOP_ADMIN_PAGE: Default admin page URL for desktop installations.
        DEFAULT_ROUTER_ADMIN_PAGE: Default admin page URL for router installations.
    """
    
    # Button locators for Mudfish web interface
    STOP_BUTTON_ID = (By.ID, "mudwd-vpn-stop-btn")
    START_BUTTON_ID = (By.ID, "mudwd-vpn-start-btn")
    
    # Default admin page URLs
    DEFAULT_DESKTOP_ADMIN_PAGE = "http://127.0.0.1:8282/signin.html"
    DEFAULT_ROUTER_ADMIN_PAGE = "http://192.168.1.1:8282/signin.html"
    
    def __init__(self, web_driver: Optional[ChromeDriver] = None) -> None:
        """
        Initialize a MudfishConnection instance.
        
        Args:
            web_driver (Optional[ChromeDriver]): ChromeDriver instance for web automation.
                                               If None, only HTTP-based methods will be available.
        """
        self._web_driver = web_driver
    
    @property
    def web_driver(self) -> Optional[ChromeDriver]:
        """
        Get the WebDriver instance.
        
        Returns:
            Optional[ChromeDriver]: The WebDriver instance if available, None otherwise.
        """
        return self._web_driver

    def login(
        self,
        username: str,
        password: str,
        adminpage: Optional[str] = None
    ) -> None:
        """
        Login to Mudfish VPN using Selenium WebDriver automation.
        
        This method performs a web-based login by navigating to the Mudfish
        admin page and filling in the username and password fields.
        
        Args:
            username (str): The username for the Mudfish account.
            password (str): The password for the Mudfish account.
            adminpage (Optional[str]): The admin page URL. If None, uses the
                                     default desktop admin page.
        
        Note:
            This method requires a WebDriver instance to be initialized.
            If no WebDriver is available, a warning will be logged and the
            method will return without performing any action.
        
        Example:
            >>> connection = MudfishConnection(web_driver)
            >>> connection.login("myuser", "mypassword")
        """
        try:
            if not self.web_driver:
                logger.warning("WebDriver not initialized for Selenium login attempt.")
                return

            logger.info("Logging into Mudfish host...")
            admin_url = adminpage or self.DEFAULT_DESKTOP_ADMIN_PAGE
            self.web_driver.get(admin_url)
            
            # Find and fill username field
            username_field = self.web_driver.find_element(By.ID, "username")
            username_field.send_keys(username)
            
            # Find and fill password field
            password_field = self.web_driver.find_element(By.ID, "password")
            password_field.send_keys(password)
            
            # Click the login button
            login_button = self.web_driver.find_element(By.CLASS_NAME, "btn")
            login_button.click()
            
            logger.info("Successfully logged into Mudfish")
            
        except WebDriverException as e:
            logger.exception("An error occurred while trying to connect to Mudfish: %s", e)

    def login_without_driver(
        self,
        username: str,
        password: str,
        adminpage: Optional[str] = None
    ) -> bool:
        """
        Login to Mudfish VPN using direct HTTP requests without WebDriver.
        
        This method performs a headless login by making HTTP requests directly
        to the Mudfish admin page, handling CSRF tokens and form submission
        automatically.
        
        Args:
            username (str): The username for the Mudfish account.
            password (str): The password for the Mudfish account.
            adminpage (Optional[str]): The admin page URL. If None, uses the
                                     default desktop admin page.
        
        Returns:
            bool: True if login is successful, False otherwise.
        
        Example:
            >>> connection = MudfishConnection()
            >>> success = connection.login_without_driver("myuser", "mypassword")
            >>> if success:
            ...     print("Login successful!")
        """
        session = requests.Session()
        login_url = adminpage or self.DEFAULT_DESKTOP_ADMIN_PAGE
        
        # Prepare login payload
        payload = {
            "username": username,
            "password": password,
            "_submit": "1"  # Often needed for form submissions
        }

        try:
            # First GET request to retrieve any CSRF tokens or cookies
            response = session.get(login_url)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract any hidden form fields (CSRF tokens, etc.)
            for hidden_input in soup.find_all('input', type='hidden'):
                if hidden_input.get('name') and hidden_input.get('value'):
                    payload[hidden_input['name']] = hidden_input['value']

            # Submit login form
            post_response = session.post(login_url, data=payload)

            # Determine login success based on response
            response_text = post_response.text.lower()
            
            # Check for various success indicators
            success_indicators = [
                "you are logged in",
                "welcome",
                "dashboard",
                "logout",
                "sign out",
                "success",
                "logged in successfully"
            ]
            
            # Check if any success indicator is present
            login_success = any(indicator in response_text for indicator in success_indicators)
            
            # Check for redirect (common success indicator)
            has_redirect = bool(post_response.history)
            
            # Check if we're still on the login page (failure indicator)
            still_on_login = "signin" in post_response.url.lower() or "login" in post_response.url.lower()
            
            if login_success or (has_redirect and not still_on_login):
                logger.info("Successfully logged into Mudfish without driver")
                return True
            elif post_response.status_code == 200 and not still_on_login:
                # If we got a 200 response and we're not on the login page, assume success
                logger.info("Login appears successful (200 response, not on login page)")
                return True
            else:
                logger.warning(
                    "Failed to log in to Mudfish without driver. Status: %s, URL: %s, Response: %s",
                    post_response.status_code,
                    post_response.url,
                    post_response.text[:200]
                )
                return False
                
        except requests.exceptions.RequestException as e:
            logger.exception("An error occurred during headless login: %s", e)
            return False

    def connect(self) -> None:
        """
        Connect to Mudfish VPN.
        
        This method attempts to start a Mudfish VPN connection by clicking
        the connect button on the web interface. It checks the current
        connection status and only attempts to connect if not already connected.
        
        Note:
            This method requires a WebDriver instance to be initialized.
            If no WebDriver is available, a warning will be logged and the
            method will return without performing any action.
        
        Example:
            >>> connection = MudfishConnection(web_driver)
            >>> connection.connect()
        """
        if not self.web_driver:
            logger.warning("WebDriver not initialized for Selenium connect attempt.")
            return
        
        logger.info("Checking Connection status...")
        connect_button = self.get_connect_button()
        
        if connect_button:
            logger.info("Starting Mudfish connection...")
            connect_button.click()

            if self.is_mudfish_connected():
                logger.info("Mudfish connection started successfully!")
            else:
                logger.error("Mudfish connection could not be started!")
        else:
            logger.info("Mudfish connection is already started!")

    def disconnect(self) -> None:
        """
        Disconnect from Mudfish VPN.
        
        This method attempts to stop the current Mudfish VPN connection by
        clicking the disconnect button on the web interface. It checks the
        current connection status and only attempts to disconnect if currently connected.
        
        Note:
            This method requires a WebDriver instance to be initialized.
            If no WebDriver is available, a warning will be logged and the
            method will return without performing any action.
        
        Example:
            >>> connection = MudfishConnection(web_driver)
            >>> connection.disconnect()
        """
        if not self.web_driver:
            logger.warning("WebDriver not initialized for Selenium disconnect attempt.")
            return
        
        logger.info("Checking Connection status...")
        disconnect_button = self.get_disconnect_button()
        
        if disconnect_button:
            logger.info("Stopping Mudfish connection...")
            disconnect_button.click()

            if self.is_mudfish_disconnected():
                logger.info("Mudfish connection stopped successfully!")
            else:
                logger.error("Mudfish connection could not be stopped!")
        else:
            logger.info("Mudfish connection is already stopped!")

    def is_mudfish_connected(self) -> bool:
        """
        Check if Mudfish VPN is currently connected.
        
        This method determines the connection status by looking for the
        presence of the disconnect button, which indicates an active connection.
        
        Returns:
            bool: True if Mudfish is connected, False otherwise.
        
        Example:
            >>> connection = MudfishConnection(web_driver)
            >>> if connection.is_mudfish_connected():
            ...     print("VPN is connected")
        """
        if not self.web_driver:
            return False
        return bool(self.get_disconnect_button(use_stop_condition=True))

    def is_mudfish_disconnected(self) -> bool:
        """
        Check if Mudfish VPN is currently disconnected.
        
        This method determines the disconnection status by looking for the
        presence of the connect button, which indicates no active connection.
        
        Returns:
            bool: True if Mudfish is disconnected, False otherwise.
        
        Example:
            >>> connection = MudfishConnection(web_driver)
            >>> if connection.is_mudfish_disconnected():
            ...     print("VPN is disconnected")
        """
        if not self.web_driver:
            return True
        return bool(self.get_connect_button(use_start_condition=True))

    def get_connect_button(
        self, 
        use_start_condition: bool = False, 
        poll_time: int = 5
    ) -> Optional[WebElement]:
        """
        Find and return the Mudfish connect button element.
        
        This method locates the connect button on the Mudfish web interface
        using either explicit waiting or implicit waiting strategies.
        
        Args:
            use_start_condition (bool, optional): If True, uses WebDriverWait
                                                with expected conditions.
                                                Defaults to False.
            poll_time (int, optional): Time in seconds to wait for the element.
                                    Defaults to 5.
        
        Returns:
            Optional[WebElement]: The connect button element if found and visible,
                                None otherwise.
        
        Example:
            >>> connection = MudfishConnection(web_driver)
            >>> button = connection.get_connect_button()
            >>> if button:
            ...     button.click()
        """
        if not self.web_driver:
            return None
            
        try:
            if use_start_condition:
                start_condition = EC.presence_of_element_located(self.START_BUTTON_ID)
                connect_button = WebDriverWait(self.web_driver, poll_time).until(start_condition)
            else:
                self.web_driver.implicitly_wait(poll_time)
                connect_button = self.web_driver.find_element(*self.START_BUTTON_ID)

            if connect_button.is_displayed():
                return connect_button

        except (TimeoutException, NoSuchElementException):
            logger.debug("No `Connect` button found!")

        return None

    def get_disconnect_button(
        self, 
        use_stop_condition: bool = False, 
        poll_time: int = 5
    ) -> Optional[WebElement]:
        """
        Find and return the Mudfish disconnect button element.
        
        This method locates the disconnect button on the Mudfish web interface
        using either explicit waiting or implicit waiting strategies.
        
        Args:
            use_stop_condition (bool, optional): If True, uses WebDriverWait
                                               with expected conditions.
                                               Defaults to False.
            poll_time (int, optional): Time in seconds to wait for the element.
                                    Defaults to 5.
        
        Returns:
            Optional[WebElement]: The disconnect button element if found and visible,
                                None otherwise.
        
        Example:
            >>> connection = MudfishConnection(web_driver)
            >>> button = connection.get_disconnect_button()
            >>> if button:
            ...     button.click()
        """
        if not self.web_driver:
            return None
            
        try:
            if use_stop_condition:
                stop_condition = EC.presence_of_element_located(self.STOP_BUTTON_ID)
                disconnect_button = WebDriverWait(self.web_driver, poll_time).until(stop_condition)
            else:
                self.web_driver.implicitly_wait(poll_time)
                disconnect_button = self.web_driver.find_element(*self.STOP_BUTTON_ID)

            if disconnect_button.is_displayed():
                return disconnect_button

        except (TimeoutException, NoSuchElementException):
            logger.debug("No `Disconnect` button found!")

        return None
