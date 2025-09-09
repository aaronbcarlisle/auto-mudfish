"""
Mudfish process management module.

This module provides functionality to detect, launch, and manage the Mudfish
VPN process on Windows systems. It handles both the executable and shortcut
launcher methods for starting Mudfish.
"""

from typing import Optional
import os
import time
import logging
import psutil
from pathlib import Path

from win32com import client

# Configure logging
logger = logging.getLogger("auto_mudfish.process")

def is_running_as_admin() -> bool:
    """
    Check if the current process is running with administrator privileges.
    
    Returns:
        bool: True if running as administrator, False otherwise.
    """
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False


class MudfishProcess:
    """
    Manages Mudfish VPN process detection and launching.
    
    This class provides methods to check if Mudfish is running, find the
    appropriate launcher (executable or shortcut), and start the Mudfish
    process with proper error handling and status monitoring.
    
    Attributes:
        MUDRUN_EXE: Default path to the Mudfish executable.
    """
    
    # Default Mudfish executable path
    MUDRUN_EXE = "C:/Program Files (x86)/Mudfish Cloud VPN/mudrun.exe"

    def __init__(self) -> None:
        """
        Initialize a MudfishProcess instance.
        
        Sets up internal state for caching executable and launcher paths.
        """
        self._mudrun_exe: Optional[str] = None
        self._mudfish_launcher_lnk: Optional[str] = None

    @property
    def mudrun_exe(self) -> str:
        """
        Get the path to the Mudfish executable.
        
        Returns:
            str: Path to the mudrun.exe executable.
        """
        if not self._mudrun_exe:
            self._mudrun_exe = self.MUDRUN_EXE
        return self._mudrun_exe

    @property
    def mudfish_launcher_lnk(self) -> str:
        """
        Get the path to the Mudfish launcher shortcut.
        
        This property dynamically constructs the path to the Mudfish launcher
        shortcut in the Start Menu using Windows Shell COM interface.
        
        Returns:
            str: Path to the Mudfish Launcher.lnk shortcut.
        
        Note:
            The shortcut method is preferred over direct executable execution
            due to potential HTTP 500 errors that can be resolved by using
            the shortcut instead of command-line arguments.
        """
        if not self._mudfish_launcher_lnk:
            # Use Windows Shell to get Start Menu path
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
        Check if the Mudfish VPN process is currently running.
        
        This method scans all running processes to determine if the
        mudrun.exe process is active.
        
        Returns:
            bool: True if Mudfish is running, False otherwise.
        
        Example:
            >>> if MudfishProcess.is_mudfish_running():
            ...     logger.info("Mudfish is already running")
        """
        # Check all running processes for mudrun.exe
        is_running = "mudrun.exe" in (p.name() for p in psutil.process_iter())
        logger.info("Mudfish %s running!", "is" if is_running else "is NOT")
        return is_running

    def start_mudfish_launcher(
        self,
        poll_time: int = 10,
        mudfish_launcher: Optional[str] = None
    ) -> bool:
        """
        Start the Mudfish VPN launcher if it's not already running.
        
        This method attempts to launch Mudfish using either the provided
        launcher path or by automatically finding the appropriate launcher.
        It includes polling to verify the process starts successfully.
        
        Args:
            poll_time (int, optional): Time in seconds to wait for Mudfish
                                     to start after launching. Defaults to 10.
            mudfish_launcher (Optional[str]): Custom path to the Mudfish launcher.
                                            If None, will auto-detect the launcher.
        
        Returns:
            bool: True if Mudfish is running or was successfully started,
                 False otherwise.
        
        Example:
            >>> process = MudfishProcess()
            >>> if process.start_mudfish_launcher():
            ...     logger.info("Mudfish started successfully")
        """
        # Early return if Mudfish is already running
        if self.is_mudfish_running():
            return True

        # Find the appropriate launcher
        launcher_path = mudfish_launcher or self.find_mudfish_launcher()
        if not launcher_path:
            return False

        # Attempt to start the Mudfish launcher with -B flag to prevent browser opening
        try:
            # Try to launch with -B flag to prevent browser opening
            if launcher_path.endswith('.lnk'):
                # For shortcut files, we need to modify the target
                import subprocess
                # Extract the target from the shortcut and add -B flag
                shell = client.Dispatch("WScript.Shell")
                shortcut = shell.CreateShortcut(launcher_path)
                target_path = shortcut.TargetPath
                working_dir = shortcut.WorkingDirectory
                
                # Launch with -B flag to prevent browser opening
                subprocess.Popen([target_path, "-B"], cwd=working_dir)
                logger.info("Launched Mudfish launcher with -B flag: %s", target_path)
            else:
                # For direct executable, add -B flag
                import subprocess
                subprocess.Popen([launcher_path, "-B"])
                logger.info("Launched Mudfish launcher with -B flag: %s", launcher_path)
        except OSError as e:
            if e.winerror == 740:
                if is_running_as_admin():
                    logger.error("Failed to start Mudfish launcher: %s. Even with administrator privileges, Mudfish failed to start.", e)
                    logger.error("This may indicate a Mudfish installation issue or permission problem.")
                else:
                    logger.error("Failed to start Mudfish launcher: %s. This operation requires elevation (Run as Administrator).", e)
                    logger.error("Mudfish requires administrator privileges to modify network settings.")
                    logger.error("Please run this application as Administrator or use the provided run_as_admin scripts.")
                raise  # Re-raise to be caught by the worker thread
            else:
                logger.error("Failed to start Mudfish launcher: %s", e)
                return False

        # Poll to verify the process started successfully
        if self.poll_is_mudfish_running(poll_time=poll_time):
            return True

        logger.error("Could not start Mudfish!")
        return False

    def poll_is_mudfish_running(self, poll_time: int = 10) -> bool:
        """
        Poll to check if Mudfish is running over a specified time period.
        
        This method checks the Mudfish process status every second for the
        specified duration to determine if the process has started successfully.
        
        Args:
            poll_time (int, optional): Time in seconds to poll for the process.
                                    Defaults to 10.
        
        Returns:
            bool: True if Mudfish is detected as running within the poll time,
                 False otherwise.
        
        Example:
            >>> process = MudfishProcess()
            >>> if process.poll_is_mudfish_running(poll_time=15):
            ...     logger.info("Mudfish started within 15 seconds")
        """
        # Check if Mudfish is running every second for the specified duration
        for _ in range(poll_time):
            time.sleep(1)  # Wait one second between each attempt
            if self.is_mudfish_running():
                return True
        return False

    def find_mudfish_launcher(self) -> Optional[str]:
        """
        Find the appropriate Mudfish launcher executable or shortcut.
        
        This method searches for the Mudfish launcher in the following order:
        1. Mudfish Launcher shortcut (.lnk) in Start Menu - requires elevation
        2. Headless executable (mudrun_headless.exe) in Program Files - requires elevation
           - C:\\Program Files (x86)\\Mudfish Cloud VPN\\mudrun_headless.exe (32-bit)
           - C:\\Program Files\\Mudfish Cloud VPN\\mudrun_headless.exe (64-bit)
        3. Direct executable (mudrun.exe) in Program Files - requires elevation
           - C:\\Program Files (x86)\\Mudfish Cloud VPN\\mudrun.exe (32-bit)
           - C:\\Program Files\\Mudfish Cloud VPN\\mudrun.exe (64-bit)
           - Alternative installation paths
        4. Fallback executable path
        
        Returns:
            Optional[str]: Path to the found launcher if available, None otherwise.
        
        Example:
            >>> process = MudfishProcess()
            >>> launcher = process.find_mudfish_launcher()
            >>> if launcher:
            ...     logger.info(f"Found launcher at: {launcher}")
        """
        logger.info("Finding Mudfish Launcher...")

        # Priority order: Shortcut first (user's preferred method), then direct executables
        # Check locations in order of preference
        locations_to_check = [
            self.mudfish_launcher_lnk,  # Shortcut - user's preferred method
            r"C:\Program Files (x86)\Mudfish Cloud VPN\mudrun_headless.exe",  # Headless version
            r"C:\Program Files\Mudfish Cloud VPN\mudrun_headless.exe",        # 64-bit headless version
            r"C:\Program Files (x86)\Mudfish Cloud VPN\mudrun.exe",           # 32-bit installation
            r"C:\Program Files\Mudfish Cloud VPN\mudrun.exe",                 # 64-bit installation
            r"C:\Program Files (x86)\Mudfish\mudrun.exe",                     # Alternative 32-bit path
            r"C:\Program Files\Mudfish\mudrun.exe",                           # Alternative 64-bit path
            self.mudrun_exe  # Fallback path
        ]
        
        for location in locations_to_check:
            if os.path.exists(location):
                logger.info("Found Mudfish launcher: %s", location)
                return location

        # If none found, log all checked locations
        locations_checked = "\n- ".join(locations_to_check)
        logger.error(
            "Could not find Mudfish Launcher!\n"
            "Locations checked:\n"
            "- %s\n",
            locations_checked
        )
        return None

