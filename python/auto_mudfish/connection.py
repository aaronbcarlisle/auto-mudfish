# type-hinting
from typing import Optional

# built-in
import logging

# third-party
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException

# internal
from driver import ChromeDriver

# logging
logger = logging.getLogger("auto_mudfish.connection")


class MudfishConnection:

    STOP_BUTTON_ID = (By.ID, "mudwd-vpn-stop-btn")
    START_BUTTON_ID = (By.ID, "mudwd-vpn-start-btn")

    DEFAULT_DESKTOP_ADMIN_PAGE = "http://127.0.0.1:8282/signin.html"
    DEFAULT_ROUTER_ADMIN_PAGE = "http://192.168.1.1:8282/signin.html"

    @property
    def web_driver(self):
        return self._web_driver

    def __init__(self, web_driver=None):

        # default to ChromeDriver
        self._web_driver = web_driver or ChromeDriver()

    def login(
            self,
            username: str,
            password: str,
            adminpage: Optional[str] = None,

    ) -> None:
        """
        Login to Mudfish using username and password.

        :param username: The username for the Mudfish account
        :param password: The password for the Mudfish account
        :param adminpage: The Admin Page url to the Mudfish login page
        """
        try:
            logger.info("Logging into Mudfish host...")
            self.web_driver.get(adminpage or self.DEFAULT_DESKTOP_ADMIN_PAGE)
            self.web_driver.find_element(By.ID, "username").send_keys(username)
            self.web_driver.find_element(By.ID, "password").send_keys(password)
            self.web_driver.find_element(By.CLASS_NAME, "btn").click()
            logger.info("Successfully logged into Mudfish")
        except WebDriverException:
            logger.exception(f"An error occurred while trying to connect to Mudfish:")

    def connect(self) -> None:
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

    def is_mudfish_connected(self):
        return self.get_disconnect_button(use_stop_condition=True)

    def is_mudfish_disconnected(self):
        return self.get_connect_button(use_start_condition=True)

    def get_connect_button(self, use_start_condition: bool = False, poll_time: int = 5):
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

    def get_disconnect_button(self, use_stop_condition: bool = False, poll_time: int = 5):
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
