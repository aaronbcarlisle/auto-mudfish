
"""
Unit tests for the Mudfish process management module.

This module contains tests for the MudfishProcess class and related functionality
including process detection, launcher management, and process control.
"""

import unittest
from unittest.mock import patch, MagicMock
import os

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from auto_mudfish.process import MudfishProcess

class TestMudfishProcess(unittest.TestCase):
    """Test cases for Mudfish process management functionality."""

    @patch('psutil.process_iter')
    def test_is_mudfish_running_true(self, mock_process_iter):
        mock_process = MagicMock()
        mock_process.name.return_value = 'mudrun.exe'
        mock_process_iter.return_value = [mock_process]
        self.assertTrue(MudfishProcess.is_mudfish_running())

    @patch('psutil.process_iter')
    def test_is_mudfish_running_false(self, mock_process_iter):
        mock_process = MagicMock()
        mock_process.name.return_value = 'other.exe'
        mock_process_iter.return_value = [mock_process]
        self.assertFalse(MudfishProcess.is_mudfish_running())

    @patch('psutil.process_iter')
    def test_is_mudfish_running_empty(self, mock_process_iter):
        mock_process_iter.return_value = []
        self.assertFalse(MudfishProcess.is_mudfish_running())


    @patch('os.path.exists')
    @patch('win32com.client')
    def test_find_mudfish_launcher_lnk_exists(self, mock_win32_client, mock_os_path_exists):
        mock_os_path_exists.side_effect = lambda x: x == 'C:/Users/test/Start Menu/Mudfish Cloud VPN/Mudfish Launcher.lnk'
        mock_shell_app = MagicMock()
        mock_shell_app.namespace.return_value.self.path = 'C:/Users/test/Start Menu'
        mock_win32_client.Dispatch.return_value = mock_shell_app

        process = MudfishProcess()
        # Manually set _mudfish_launcher_lnk to avoid re-mocking path operations for its property
        process._mudfish_launcher_lnk = 'C:/Users/test/Start Menu/Mudfish Cloud VPN/Mudfish Launcher.lnk'

        self.assertEqual(process.find_mudfish_launcher(), 'C:/Users/test/Start Menu/Mudfish Cloud VPN/Mudfish Launcher.lnk')
        mock_os_path_exists.assert_any_call('C:/Users/test/Start Menu/Mudfish Cloud VPN/Mudfish Launcher.lnk')

    @patch('os.path.exists')
    @patch('win32com.client')
    def test_find_mudfish_launcher_exe_fallback(self, mock_win32_client, mock_os_path_exists):
        mock_os_path_exists.side_effect = lambda x: x == MudfishProcess.MUDRUN_EXE # LNK does not exist, EXE does
        mock_shell_app = MagicMock()
        mock_shell_app.namespace.return_value.self.path = 'C:/Users/test/Start Menu'
        mock_win32_client.Dispatch.return_value = mock_shell_app

        process = MudfishProcess()
        # Manually set _mudfish_launcher_lnk to avoid re-mocking path operations for its property
        process._mudfish_launcher_lnk = 'C:/Users/test/Start Menu/Mudfish Cloud VPN/Mudfish Launcher.lnk'

        self.assertEqual(process.find_mudfish_launcher(), MudfishProcess.MUDRUN_EXE)
        mock_os_path_exists.assert_any_call('C:/Users/test/Start Menu/Mudfish Cloud VPN/Mudfish Launcher.lnk')
        mock_os_path_exists.assert_any_call(MudfishProcess.MUDRUN_EXE)

    @patch('os.path.exists')
    @patch('win32com.client')
    @patch('auto_mudfish.process.logger') # Mock the logger to check error messages
    def test_find_mudfish_launcher_not_found(self, mock_logger, mock_win32_client, mock_os_path_exists):
        mock_os_path_exists.return_value = False # Neither exists
        mock_shell_app = MagicMock()
        mock_shell_app.namespace.return_value.self.path = 'C:/Users/test/Start Menu'
        mock_win32_client.Dispatch.return_value = mock_shell_app

        process = MudfishProcess()
        # Manually set _mudfish_launcher_lnk to avoid re-mocking path operations for its property
        process._mudfish_launcher_lnk = 'C:/Users/test/Start Menu/Mudfish Cloud VPN/Mudfish Launcher.lnk'

        self.assertIsNone(process.find_mudfish_launcher())
        mock_logger.error.assert_called_once()


    @patch('auto_mudfish.process.MudfishProcess.is_mudfish_running')
    @patch('auto_mudfish.process.MudfishProcess.find_mudfish_launcher')
    @patch('os.startfile')
    @patch('auto_mudfish.process.MudfishProcess.poll_is_mudfish_running')
    def test_start_mudfish_launcher_already_running(self, mock_poll_running, mock_startfile, mock_find_launcher, mock_is_running):
        mock_is_running.return_value = True
        process = MudfishProcess()
        self.assertTrue(process.start_mudfish_launcher())
        mock_is_running.assert_called_once()
        mock_find_launcher.assert_not_called()
        mock_startfile.assert_not_called()
        mock_poll_running.assert_not_called()

    @patch('auto_mudfish.process.MudfishProcess.is_mudfish_running')
    @patch('auto_mudfish.process.MudfishProcess.find_mudfish_launcher')
    @patch('os.startfile')
    @patch('auto_mudfish.process.MudfishProcess.poll_is_mudfish_running')
    def test_start_mudfish_launcher_found_and_started(self, mock_poll_running, mock_startfile, mock_find_launcher, mock_is_running):
        mock_is_running.side_effect = [False, True]  # Not running initially, but becomes running after poll
        mock_find_launcher.return_value = 'C:/path/to/mudfish_launcher.lnk'
        mock_poll_running.return_value = True

        process = MudfishProcess()
        self.assertTrue(process.start_mudfish_launcher())

        mock_is_running.assert_called_once() # Initial check
        mock_find_launcher.assert_called_once()
        mock_startfile.assert_called_once_with('C:/path/to/mudfish_launcher.lnk')
        mock_poll_running.assert_called_once_with(poll_time=10)

    @patch('auto_mudfish.process.MudfishProcess.is_mudfish_running')
    @patch('auto_mudfish.process.MudfishProcess.find_mudfish_launcher')
    @patch('os.startfile')
    @patch('auto_mudfish.process.MudfishProcess.poll_is_mudfish_running')
    @patch('auto_mudfish.process.logger')
    def test_start_mudfish_launcher_not_found(self, mock_logger, mock_poll_running, mock_startfile, mock_find_launcher, mock_is_running):
        mock_is_running.return_value = False
        mock_find_launcher.return_value = None

        process = MudfishProcess()
        self.assertFalse(process.start_mudfish_launcher())

        mock_is_running.assert_called_once()
        mock_find_launcher.assert_called_once()
        mock_startfile.assert_not_called()
        mock_poll_running.assert_not_called()
        mock_logger.error.assert_not_called()

    @patch('auto_mudfish.process.MudfishProcess.is_mudfish_running')
    @patch('auto_mudfish.process.MudfishProcess.find_mudfish_launcher')
    @patch('os.startfile')
    @patch('auto_mudfish.process.MudfishProcess.poll_is_mudfish_running')
    @patch('auto_mudfish.process.logger')
    def test_start_mudfish_launcher_failed_to_poll(self, mock_logger, mock_poll_running, mock_startfile, mock_find_launcher, mock_is_running):
        mock_is_running.return_value = False # Not running initially
        mock_find_launcher.return_value = 'C:/path/to/mudfish_launcher.lnk'
        mock_poll_running.return_value = False # Never becomes running

        process = MudfishProcess()
        self.assertFalse(process.start_mudfish_launcher())

        mock_is_running.assert_called_once()
        mock_find_launcher.assert_called_once()
        mock_startfile.assert_called_once_with('C:/path/to/mudfish_launcher.lnk')
        mock_poll_running.assert_called_once_with(poll_time=10)
        mock_logger.error.assert_called_once_with("Could not start Mudfish!")

    @patch('time.sleep')
    @patch('auto_mudfish.process.MudfishProcess.is_mudfish_running')
    def test_poll_is_mudfish_running_success(self, mock_is_running, mock_sleep):
        mock_is_running.side_effect = [False, False, True] # Becomes true after 2 seconds
        process = MudfishProcess()
        self.assertTrue(process.poll_is_mudfish_running(poll_time=5))
        self.assertEqual(mock_is_running.call_count, 3)
        self.assertEqual(mock_sleep.call_count, 3)

    @patch('time.sleep')
    @patch('auto_mudfish.process.MudfishProcess.is_mudfish_running')
    def test_poll_is_mudfish_running_failure(self, mock_is_running, mock_sleep):
        mock_is_running.return_value = False # Never becomes true
        process = MudfishProcess()
        self.assertFalse(process.poll_is_mudfish_running(poll_time=3))
        self.assertEqual(mock_is_running.call_count, 3)
        self.assertEqual(mock_sleep.call_count, 3)
