# - built-in -
import os
import sys
import time
import logging
import argparse
import psutil
from pathlib import Path
from typing import Optional

# - third-party -
from win32com import client

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException, SessionNotCreatedException

# - logging -
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mudfish-auto")

# - mudfish defaults -
DEFAULT_MUDFISH_EXE_PATH = "C:/Program Files (x86)/Mudfish Cloud VPN/mudrun.exe"

DEFAULT_MUDFISH_DESKTOP_URL = "http://127.0.0.1:8282/signin.html"
DEFAULT_MUDFISH_ROUTER_URL = "http://192.168.1.1:8282"

MUDFISH_STOP_BUTTON_ID = (By.ID, "mudwd-vpn-stop-btn")
MUDFISH_START_BUTTON_ID = (By.ID, "mudwd-vpn-start-btn")

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("headless")


def get_chrome_driver():
    try:
        return webdriver.Chrome(options=chrome_options)
    except SessionNotCreatedException:
        logger.warning("No Chrome Driver found!")
        return None


def install_chrome_driver():
    from get_chrome_driver import GetChromeDriver

    # install the chrome driver
    chrome_driver = GetChromeDriver()
    chrome_driver.install()

    # return a new instance to use later
    return webdriver.Chrome(options=chrome_options)


def prompt_install_chrome_driver():
    import tkinter

    # create root window instance and hide it
    root = tkinter.Tk()
    root.withdraw()

    try:
        return webdriver.Chrome(options=chrome_options)
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


def is_mudfish_running() -> bool:
    """
    Check if Mudfish is running.
    :return: True if Mudfish is running, False otherwise
    """
    # loop through available processes to find the `mudrun` process
    return "mudrun.exe" in (p.name() for p in psutil.process_iter())


def ensure_mudfish_is_running(
        polling_range: Optional[int] = 10,
        launcher: Optional[str] = None
) -> bool:
    """
    Ensure Mudfish is running. If Mudfish is not running, it attempts to start it.
    :param polling_range: Pulling option when waiting for Mudfish to launch (default is 10 seconds).
    :param launcher: Optional path to the Mudfish Launcher executable.
    :return: True if Mudfish is running or was successfully started, False otherwise
    """

    # early return if mudfish is already running
    if is_mudfish_running():
        logger.info("Mudfish is already running, ...")
        return True

    # otherwise attempt to find and run the Mudfish Launcher
    logger.info("Finding Mudfish Launcher...")

    # NOTE: The mudfish documentation mentions a http 500 error which can be
    # resolved by using a -S with the exe, however this requires firewall and
    # permission updates, using the `lnk` shortcut in the Start Menu seems to be
    # the most reliable way of launching Mudfish successfully via commandline
    shell_app = client.Dispatch("Shell.Application")
    mudfish_lnk = Path(shell_app.namespace(2).self.path).joinpath(
        "Mudfish Cloud VPN",
        "Mudfish Launcher.lnk"
    ).as_posix()  # converts to forward slashes

    launcher = launcher or mudfish_lnk if os.path.exists(mudfish_lnk) else DEFAULT_MUDFISH_EXE_PATH
    if not os.path.exists(launcher):
        locations = [mudfish_lnk, DEFAULT_MUDFISH_EXE_PATH]
        locations_checked = "\n- ".join(locations)
        logger.error(
            f"Could not find Mudfish Launcher!\n"
            f"Locations checked:\n"
            f"- {locations_checked}\n"
        )
        return False

    # start the mudfish launcher
    os.startfile(launcher)

    # check if mudfish is running every second for up to 10 seconds
    for _ in range(polling_range):
        time.sleep(1)  # Wait a second between each attempt
        if is_mudfish_running():

            logger.info("Mudfish is now running!")
            return True

    # log and return false if the mudfish process was not found running after 10 seconds
    logger.error("Could not start Mudfish!")
    return False


def login_and_connect_to_mudfish(
        username: str,
        password: str,
        adminpage: str,
        chrome_driver: Optional[webdriver.Chrome] = None
) -> None:
    """
    Connect to Mudfish using Selenium WebDriver.
    :param username: The username for the Mudfish account
    :param password: The password for the Mudfish account
    :param adminpage: The Admin Page url to the Mudfish login page
    :param chrome_driver: Chrome ``webdriver`` instance (new instance if None is given).
    """
    try:
        chrome_driver = chrome_driver or webdriver.Chrome(options=chrome_options)

        logger.info("Logging into Mudfish host...")
        chrome_driver.get(adminpage)
        chrome_driver.find_element(By.ID, "username").send_keys(username)
        chrome_driver.find_element(By.ID, "password").send_keys(password)
        chrome_driver.find_element(By.CLASS_NAME, "btn").click()
        logger.info("Successfully logged into Mudfish")

        logger.info("Checking Connection status...")
        try:
            # if the stop button is available then Mudfish is already connected
            stop_condition = EC.presence_of_element_located(MUDFISH_STOP_BUTTON_ID)
            WebDriverWait(chrome_driver, 4).until(stop_condition)

            logger.info("Mudfish is already connected!")
        except TimeoutException:
            logger.info("Attempting to connect Mudfish VPN...")

            # wait for the start button to show
            start_condition = EC.presence_of_element_located(MUDFISH_START_BUTTON_ID)
            connect_button = WebDriverWait(chrome_driver, 4).until(start_condition)

            # click the start button if available
            if connect_button.is_displayed():
                connect_button.click()
                logger.info("Mudfish is now connected!")
        finally:
            chrome_driver.quit()  # ensure the chrome driver is terminated
    except WebDriverException:
        logger.exception(f"An error occurred while trying to connect to Mudfish:")


def main(
        username: str,
        password: str,
        adminpage: str,
        launcher: Optional[str] = None
) -> None:
    """
    Main function that ensures Mudfish is running and then connects to it.
    :param username: The username for the Mudfish account
    :param password: The password for the Mudfish account
    :param adminpage: Optional admin page url.
    :param launcher: Optional path to the Mudfish Launcher.
    """

    # early return if mudfish could not be ran successfully
    if not ensure_mudfish_is_running(launcher=launcher):
        logger.error("Mudfish is not running and could not be ran. Aborting!")
        return

    # ensure the chrome driver is installed
    chrome_driver = get_chrome_driver()

    # early return if no chrome driver was found/installed
    chrome_driver = chrome_driver or prompt_install_chrome_driver()
    if not chrome_driver:
        logger.warning("Chrome Driver is needed to continue, aborting!")
        return

    # login and connect to mudfish
    login_and_connect_to_mudfish(
        username,
        password,
        adminpage,
        chrome_driver=chrome_driver
    )


if __name__ == "__main__":
    # setup arg parser
    parser = argparse.ArgumentParser(description="Auto-connect Mudfish")

    # required args
    parser.add_argument("-u", "--username", type=str, required=True, help="Username to Mudfish account.")
    parser.add_argument("-p", "--password", type=str, required=True, help="Password to Mudfish account.")

    # optional args
    parser.add_argument(
        "-a",
        "--adminpage",
        default=DEFAULT_MUDFISH_DESKTOP_URL,
        type=str,
        required=False,
        help=(
            f"Optional admin page url. "
            f"(Default is '{DEFAULT_MUDFISH_DESKTOP_URL}')"
        )
    )
    parser.add_argument(
        "-l",
        "--launcher",
        type=str,
        required=False,
        help=(
            f"Optional Mudfish Launcher location override. "
            f"(Default is `{DEFAULT_MUDFISH_EXE_PATH}` for Desktop.)"
        )
    )

    # pass commandline args to the main method to start process
    main_kwargs = vars(parser.parse_args())
    logger.debug(f"Parser Kwargs: '{main_kwargs}'")
    main(**main_kwargs)

    sys.exit()