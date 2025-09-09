
"""
Unit tests for the Chrome WebDriver management module.

This module contains tests for the ChromeDriver class and related functionality
including driver creation, error handling, and fallback mechanisms.
"""

import unittest
from unittest.mock import patch, MagicMock
import os

from selenium.common.exceptions import SessionNotCreatedException
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options as ChromeOptionsSelenium

from get_chrome_driver import GetChromeDriver
from auto_mudfish.driver import get_chrome_driver, ChromeDriver
from get_chrome_driver.enums.os_platform import OsPlatform


class TestDriver(unittest.TestCase):
    """Test cases for Chrome WebDriver functionality."""

    @patch('auto_mudfish.driver.GetChromeDriver')
    @patch('auto_mudfish.driver.os.path.join')
    @patch('auto_mudfish.driver.ChromeDriver')
    def test_get_chrome_driver_success(self, mock_our_chrome_driver_class, mock_os_path_join, mock_get_chrome_driver_class):
        # Setup mocks
        mock_installer_instance = MagicMock()

        # This patches the GetChromeDriver class as imported in driver.py
        mock_get_chrome_driver_class.return_value = mock_installer_instance

        # Mock the auto_download method of the *instance* returned by the mocked GetChromeDriver
        mock_installer_instance.auto_download.return_value = "/mock/driver/path"

        mock_os_path_join.return_value = "/mock/driver/path/chromedriver.exe"

        mock_chrome_driver_instance = MagicMock(spec=webdriver.Chrome)
        mock_our_chrome_driver_class.return_value = mock_chrome_driver_instance

        # Call the function under test

        driver = get_chrome_driver(headless=True)

        # Assertions
        mock_get_chrome_driver_class.assert_called_once_with(os_platform=OsPlatform.win)
        mock_installer_instance.auto_download.assert_called_once_with(extract=True) # Corrected assertion target
        mock_os_path_join.assert_called_once_with("/mock/driver/path", "chromedriver.exe")
        mock_our_chrome_driver_class.assert_called_once_with(headless=True, executable_path="/mock/driver/path/chromedriver.exe")
        self.assertEqual(driver, mock_chrome_driver_instance)

    @patch('auto_mudfish.driver.GetChromeDriver')
    @patch('auto_mudfish.driver.ChromeDriver')
    @patch('auto_mudfish.driver.os.path.join')
    @patch('auto_mudfish.driver.logger')
    def test_get_chrome_driver_session_not_created_exception(self, mock_logger, mock_os_path_join, mock_our_chrome_driver_class, mock_get_chrome_driver_class):
        # Setup mocks to raise SessionNotCreatedException
        mock_installer_instance = MagicMock()

        mock_get_chrome_driver_class.return_value = mock_installer_instance

        # Mock the auto_download method of the *instance* returned by the mocked GetChromeDriver
        mock_installer_instance.auto_download.return_value = "/mock/driver/path"

        mock_os_path_join.return_value = "/mock/driver/path/chromedriver.exe"

        mock_our_chrome_driver_class.side_effect = SessionNotCreatedException("Test exception")

        # Call the function under test

        driver = get_chrome_driver(headless=True)

        # Assertions
        mock_get_chrome_driver_class.assert_called_once_with(os_platform=OsPlatform.win)
        mock_installer_instance.auto_download.assert_called_once_with(extract=True) # Corrected assertion target
        mock_os_path_join.assert_called_once_with("/mock/driver/path", "chromedriver.exe")
        mock_our_chrome_driver_class.assert_called_once_with(headless=True, executable_path="/mock/driver/path/chromedriver.exe")
        mock_logger.warning.assert_called_once()
        # Check that the warning message contains the expected text
        warning_call = mock_logger.warning.call_args[0][0]
        self.assertIn("Failed to create Chrome WebDriver session", warning_call)
        self.assertIsNone(driver)

    @patch('selenium.webdriver.chrome.service.Service')
    @patch('selenium.webdriver.chrome.webdriver.WebDriver.__init__', return_value=None)
    @patch('auto_mudfish.driver.Options') # Patching the Options class imported in driver.py
    @patch('auto_mudfish.driver.Service')  # Patch Service where it's used in driver.py
    @patch('auto_mudfish.driver.webdriver.ChromeOptions')
    def test_chrome_driver_init_with_executable_path(self, mock_webdriver_chrome_options, mock_driver_service, mock_options_class, mock_webdriver_init, mock_service_class):
        mock_webdriver_init.return_value = None  # Mock the super().__init__ call

        executable_path = "/mock/path/chromedriver.exe"

        driver = ChromeDriver(executable_path=executable_path, headless=True)

        mock_driver_service.assert_called_once_with(executable_path=executable_path) # Correctly assert on the mock that represents Service() in driver.py
        mock_webdriver_chrome_options.assert_called_once() # This is the class being instantiated inside ChromeDriver
        mock_webdriver_init.assert_called_once_with(
            options=driver.options,
            service=mock_driver_service.return_value, # Should be the return value of the patched Service in driver.py
            keep_alive=True
        )
        # Check that headless arguments were added (including additional headless options)
        add_argument_calls = mock_webdriver_chrome_options.return_value.add_argument.call_args_list
        headless_calls = [call for call in add_argument_calls if call[0][0] == "--headless"]
        self.assertEqual(len(headless_calls), 1)
        self.assertIn("--headless", [call[0][0] for call in add_argument_calls])

    @patch('selenium.webdriver.chrome.service.Service')
    @patch('selenium.webdriver.chrome.webdriver.WebDriver.__init__', return_value=None)
    @patch('auto_mudfish.driver.Options') # Patching the Options class imported in driver.py
    @patch('auto_mudfish.driver.Service') # Patch Service where it's used in driver.py
    @patch('auto_mudfish.driver.webdriver.ChromeOptions')
    def test_chrome_driver_init_with_existing_options_and_service(self, mock_webdriver_chrome_options, mock_driver_service, mock_options_class, mock_webdriver_init, mock_service_class):
        mock_webdriver_init.return_value = None  # Mock the super().__init__ call
        mock_existing_options = MagicMock(spec=ChromeOptionsSelenium)
        mock_existing_service = MagicMock(spec=Service)

        driver = ChromeDriver(options=mock_existing_options, service=mock_existing_service, headless=False)

        mock_service_class.assert_not_called() # Existing service is passed directly
        mock_webdriver_init.assert_called_once_with(
            options=mock_existing_options,
            service=mock_existing_service,
            keep_alive=True
        )
        mock_webdriver_chrome_options.assert_not_called() # Headless is False, so default options should not be instantiated

    @patch('selenium.webdriver.chrome.service.Service')
    @patch('selenium.webdriver.chrome.webdriver.WebDriver.__init__', return_value=None)
    @patch('auto_mudfish.driver.Options') # Patching the Options class imported in driver.py
    @patch('auto_mudfish.driver.Service') # Patch Service where it's used in driver.py
    @patch('auto_mudfish.driver.webdriver.ChromeOptions')
    def test_chrome_driver_init_headless_default_options(self, mock_webdriver_chrome_options, mock_driver_service, mock_options_class, mock_webdriver_init, mock_service_class):
        mock_webdriver_init.return_value = None  # Mock the super().__init__ call

        executable_path = "/mock/path/chromedriver.exe"

        driver = ChromeDriver(executable_path=executable_path, headless=True)

        mock_webdriver_chrome_options.assert_called_once() # This is the class being instantiated inside ChromeDriver
        # Check that headless arguments were added (including additional headless options)
        add_argument_calls = mock_webdriver_chrome_options.return_value.add_argument.call_args_list
        headless_calls = [call for call in add_argument_calls if call[0][0] == "--headless"]
        self.assertEqual(len(headless_calls), 1)
        self.assertIn("--headless", [call[0][0] for call in add_argument_calls])

    @patch('selenium.webdriver.chrome.service.Service')
    @patch('selenium.webdriver.chrome.webdriver.WebDriver.__init__', return_value=None)
    @patch('auto_mudfish.driver.Options') # Patching the Options class imported in driver.py
    @patch('auto_mudfish.driver.Service') # Patch Service where it's used in driver.py
    @patch('auto_mudfish.driver.webdriver.ChromeOptions')
    def test_chrome_driver_init_no_executable_path_or_service(self, mock_webdriver_chrome_options, mock_driver_service, mock_options_class, mock_webdriver_init, mock_service_class):
        mock_webdriver_init.return_value = None  # Mock the super().__init__ call

        # Simulate a call without executable_path or service, expecting super().__init__ to handle it

        # For this test, we expect Service() to be called. So, we'll ensure Service() returns a mock.

        # mock_driver_service here is an instance, not the class. We need to patch the class.
        # The class `Service` is imported as `Service` in driver.py
        # The mock_service_class parameter already patches `selenium.webdriver.chrome.service.Service`
        # The relevant call in ChromeDriver is `Service()`, so we need to set the return value of mock_service_class
        mock_service_class.return_value = MagicMock(spec=Service)

        driver = ChromeDriver(headless=False)  # Headless is false, so options won't be modified

        mock_driver_service.assert_called_once_with() # Correctly assert on the mock that represents Service() in driver.py
        mock_options_class.assert_not_called()
        mock_webdriver_init.assert_called_once_with(
            options=None,
            service=mock_driver_service.return_value, # Should be the return value of the patched Service in driver.py
            keep_alive=True
        )
