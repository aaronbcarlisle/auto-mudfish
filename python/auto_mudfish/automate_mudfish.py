# type-hinting
from typing import Optional

# built-in
import sys
import logging
import argparse

# internal
from process import MudfishProcess
from connection import MudfishConnection
from driver import get_chrome_driver, prompt_install_chrome_driver

# logging
logger = logging.getLogger("auto_mudfish.automate_mudfish")


def auto_start(
        username: str,
        password: str,
        adminpage: Optional[str] = None,
        launcher: Optional[str] = None
) -> None:
    """
    Main function that ensures Mudfish is running and then connects to it.

    :param username: The username for the Mudfish account
    :param password: The password for the Mudfish account
    :param adminpage: Optional admin page url.
    :param launcher: Optional path to the Mudfish Launcher.
    """

    mudfish_process = MudfishProcess()
    mudfish_process_started = mudfish_process.start_mudfish_launcher(
        mudfish_launcher=launcher
    )

    # early return if mudfish could not be run successfully
    if not mudfish_process_started:
        logger.error("Mudfish is not running and could not be ran. Aborting!")
        return

    # ensure the chrome driver is installed
    chrome_driver = get_chrome_driver()

    # early return if no chrome driver was found/installed
    chrome_driver = chrome_driver or prompt_install_chrome_driver()
    if not chrome_driver:
        logger.warning("Chrome Driver is needed to continue, aborting!")
        return

    mudfish_connection = MudfishConnection(web_driver=chrome_driver)

    # login and connect to mudfish
    # noinspection PyBroadException
    try:
        mudfish_connection.login(username, password, adminpage=adminpage)
        mudfish_connection.connect()
    except Exception:
        logger.exception("")
    finally:
        mudfish_connection.web_driver.quit()


if __name__ == "__main__":
    # setup arg parser
    parser = argparse.ArgumentParser(description="Auto-connect Mudfish")

    # required args
    parser.add_argument("-u", "--username", type=str, required=True, help="Username to Mudfish account.")
    parser.add_argument("-p", "--password", type=str, required=True, help="Password to Mudfish account.")

    # optional args
    default_adminpage = MudfishConnection.DEFAULT_DESKTOP_ADMIN_PAGE
    parser.add_argument(
        "-a",
        "--adminpage",
        default=default_adminpage,
        type=str,
        required=False,
        help=(
            f"Optional admin page url. "
            f"(Default is '{default_adminpage}')"
        )
    )
    parser.add_argument(
        "-l",
        "--launcher",
        type=str,
        required=False,
        help=(
            f"Optional Mudfish Launcher location override. "
            f"(Default is `{MudfishProcess.MUDRUN_EXE}` for Desktop.)"
        )
    )

    # pass commandline args to the setup method to start process
    main_kwargs = vars(parser.parse_args())
    logger.debug(f"Parser Kwargs: '{main_kwargs}'")
    auto_start(**main_kwargs)

    sys.exit()
