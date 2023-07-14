# type-hinting
from typing import Optional, Union

# built-in
import logging

# third-party
from selenium import webdriver
from get_chrome_driver import GetChromeDriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import SessionNotCreatedException

# logging
logger = logging.getLogger("auto_mudfish.driver")


def get_chrome_driver(headless: bool = True) -> Optional[webdriver.Chrome]:
    """
    Tries to get a chrome driver instance.

    :param headless: Whether to run the Chrome driver headless or not (default is ``True``).

    :return: A chrome driver instance if successful, None otherwise.
    """
    try:
        return ChromeDriver(headless=headless)
    except SessionNotCreatedException:
        logger.warning("No Chrome Driver found!")
        return None


def install_chrome_driver() -> webdriver.Chrome:
    """
    Installs chrome driver and returns a new chrome driver instance.

    :return: A new chrome driver instance.
    """

    # install the chrome driver
    chrome_driver = GetChromeDriver()
    chrome_driver.install()

    # return a new instance to use later
    return get_chrome_driver()


def prompt_install_chrome_driver() -> Union[webdriver.Chrome, bool]:
    """
    Prompts user to install chrome driver if not found.
    Returns a new chrome driver instance if user agrees to install, False otherwise.

    :return: A new chrome driver instance if user agrees to install, False otherwise.
    """
    import tkinter

    # create root window instance and hide it
    root = tkinter.Tk()
    root.withdraw()

    try:
        return get_chrome_driver()
    except SessionNotCreatedException:
        from tkinter import messagebox

        install_missing_chrome_driver = messagebox.askyesnocancel(
            title="Chrome Driver Missing!",
            message=(
                "Chrome Driver is needed to continue!\n"
                "Would you like to install the matching Chrome Driver for your Browser?"
            ),
            default=messagebox.YES
        )

        if not install_missing_chrome_driver:
            logger.warning("Chrome Driver will not be installed, aborting...")
            return False

        return install_chrome_driver()

    # ensure the tkinter session is always terminated
    finally:
        root.destroy()


class ChromeDriver(webdriver.Chrome):

    def __init__(
            self,
            options: Options = None,
            service: Service = None,
            keep_alive: bool = True,
            headless: bool = False
    ):
        """
        Creates a new instance of the chrome driver. Starts the service and
        then creates new instance of chrome driver.

        :param options: This takes an instance of ChromeOptions
        :param service: Service object for handling the browser driver.
        :param keep_alive: Whether to configure ChromeRemoteConnection to use HTTP keep-alive.
        :param headless: Whether to run the Chrome driver headless or not (default is ``False``).
        """
        self.options = options

        # forces the Chrome Driver to run headless if specified
        if headless:
            chrome_options = self.options or webdriver.ChromeOptions()
            chrome_options.add_argument("headless")

            self.options = chrome_options

        # let it do the rest
        super().__init__(
            options=self.options,
            service=service,
            keep_alive=keep_alive
        )

