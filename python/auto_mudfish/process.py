# type-hinting
from typing import Optional

# built-in
import os
import time
import logging
import psutil
from pathlib import Path

# third-party
from win32com import client

# logging
logger = logging.getLogger("auto_mudfish.process")


class MudfishProcess:

    MUDRUN_EXE = "C:/Program Files (x86)/Mudfish Cloud VPN/mudrun.exe"

    @property
    def mudrun_exe(self):
        if not self._mudrun_exe:
            self._mudrun_exe = self.MUDRUN_EXE

        return self._mudrun_exe

    @property
    def mudfish_launcher_lnk(self):
        if not self._mudfish_launcher_lnk:
            # NOTE: The mudfish documentation mentions a http 500 error which can be
            # resolved by using a -S with the exe, however this requires firewall and
            # permission updates, using the `lnk` shortcut in the Start Menu seems to be
            # the most reliable way of launching Mudfish successfully via commandline
            shell_app = client.Dispatch("Shell.Application")
            self._mudfish_launcher_lnk = Path(shell_app.namespace(2).self.path).joinpath(
                "Mudfish Cloud VPN",
                "Mudfish Launcher.lnk"
            ).as_posix()  # converts to forward slashes

        return self._mudfish_launcher_lnk

    @classmethod
    def is_mudfish_running(cls) -> bool:
        """
        Check if Mudfish is running.

        :return: True if Mudfish is running, False otherwise
        """
        # loop through available processes to find the `mudrun` process
        is_running = "mudrun.exe" in (p.name() for p in psutil.process_iter())
        logger.info(f"Mudfish {'is' if is_running else 'is NOT'} running!")
        return is_running

    def __init__(self):
        self._mudrun_exe = None
        self._mudfish_launcher_lnk = None

    def start_mudfish_launcher(
            self,
            poll_time: int = 10,
            mudfish_launcher: Optional[str] = None
    ) -> bool:
        """
        Start the Mudfish Launcher if it isn't already started.

        :param poll_time: Poll option when waiting for Mudfish to launch (default is 10 seconds).
        :param mudfish_launcher: Optional path to the Mudfish Launcher executable.
        :return: ``True`` if Mudfish is running or was successfully started, ``False`` otherwise
        """

        # early return if mudfish is already running
        if self.is_mudfish_running():
            return True

        # try to find the mudfish launcher
        mudfish_launcher = mudfish_launcher or self.find_mudfish_launcher()

        # early return if it could not be found
        if not mudfish_launcher:
            return False

        # attempt to start the mudfish launcher
        os.startfile(mudfish_launcher)

        # give the process time to launch by doing a poll on the DOM
        if self.poll_is_mudfish_running(poll_time=poll_time):
            return True

        logger.error("Could not start Mudfish!")
        return False

    def poll_is_mudfish_running(self, poll_time: int = 10):

        # check if mudfish is running every second for up to 10 seconds
        for _ in range(poll_time):
            time.sleep(1)  # Wait a second between each attempt
            if self.is_mudfish_running():
                return True
        return False

    def find_mudfish_launcher(self):
        # otherwise attempt to find and run the Mudfish Launcher
        logger.info("Finding Mudfish Launcher...")

        mudfish_launcher = (
            self.mudfish_launcher_lnk if os.path.exists(self.mudfish_launcher_lnk)
            else self.mudrun_exe
        )

        if not os.path.exists(mudfish_launcher):
            locations = [self.mudfish_launcher_lnk, self.mudrun_exe]
            locations_checked = "\n- ".join(locations)
            logger.error(
                f"Could not find Mudfish Launcher!\n"
                f"Locations checked:\n"
                f"- {locations_checked}\n"
            )
            return None

        return mudfish_launcher

