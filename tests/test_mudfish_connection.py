
"""
Unit tests for the Mudfish connection management module.

This module contains tests for the MudfishConnection class and related functionality
including login, connection status checking, and WebDriver interactions.
"""

import unittest
from unittest.mock import patch, MagicMock
import requests
from bs4 import BeautifulSoup

from auto_mudfish.connection import MudfishConnection
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException

class TestMudfishConnection(unittest.TestCase):
    """Test cases for Mudfish connection functionality."""

    def setUp(self):
        self.connection = MudfishConnection()
        self.username = "testuser"
        self.password = "testpass"
        self.adminpage = "http://127.0.0.1:8282/signin.html"

    @patch('requests.Session')
    @patch('auto_mudfish.connection.BeautifulSoup')
    @patch('auto_mudfish.connection.logger')
    def test_login_without_driver_success_redirect(self, mock_logger, mock_bs, mock_session):
        mock_response = MagicMock()
        mock_response.status_code = 302 # Redirect
        mock_response.history = [MagicMock()] # Simulate redirect history
        mock_response.url = "http://127.0.0.1:8282/main.html"
        mock_response.text = ""

        mock_session_instance = MagicMock()
        mock_session_instance.get.return_value = MagicMock(text="<html><head></head><body><input type=\"hidden\" name=\"csrf_token\" value=\"abc\"></body></html>")
        mock_session_instance.post.return_value = mock_response
        mock_session.return_value = mock_session_instance

        self.assertTrue(self.connection.login_without_driver(self.username, self.password, self.adminpage))
        mock_logger.info.assert_called_with("Login initiated, redirected to: %s", mock_response.url)

    @patch('requests.Session')
    @patch('auto_mudfish.connection.BeautifulSoup')
    @patch('auto_mudfish.connection.logger')
    def test_login_without_driver_success_message(self, mock_logger, mock_bs, mock_session):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.history = []
        mock_response.text = "You are logged in"

        mock_session_instance = MagicMock()
        mock_session_instance.get.return_value = MagicMock(text="<html><head></head><body></body></html>")
        mock_session_instance.post.return_value = mock_response
        mock_session.return_value = mock_session_instance

        self.assertTrue(self.connection.login_without_driver(self.username, self.password, self.adminpage))
        mock_logger.info.assert_called_with("Successfully logged into Mudfish without driver")

    @patch('requests.Session')
    @patch('auto_mudfish.connection.BeautifulSoup')
    @patch('auto_mudfish.connection.logger')
    def test_login_without_driver_failure(self, mock_logger, mock_bs, mock_session):
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.history = []
        mock_response.text = "Invalid credentials"

        mock_session_instance = MagicMock()
        mock_session_instance.get.return_value = MagicMock(text="<html><head></head><body></body></html>")
        mock_session_instance.post.return_value = mock_response
        mock_session.return_value = mock_session_instance

        self.assertFalse(self.connection.login_without_driver(self.username, self.password, self.adminpage))
        mock_logger.warning.assert_called_once()

    @patch('requests.Session')
    @patch('auto_mudfish.connection.BeautifulSoup')
    @patch('auto_mudfish.connection.logger')
    def test_login_without_driver_exception(self, mock_logger, mock_bs, mock_session):
        mock_session.return_value.get.side_effect = requests.exceptions.RequestException("Test Exception")

        self.assertFalse(self.connection.login_without_driver(self.username, self.password, self.adminpage))
        mock_logger.exception.assert_called_once()

    @patch('auto_mudfish.connection.logger')
    def test_login_with_driver_not_initialized(self, mock_logger):
        self.connection = MudfishConnection(web_driver=None)
        self.connection.login(self.username, self.password, self.adminpage)
        mock_logger.warning.assert_called_with("WebDriver not initialized for Selenium login attempt.")

    @patch('selenium.webdriver.chrome.webdriver.WebDriver')
    @patch('auto_mudfish.connection.logger')
    def test_login_with_driver_success(self, mock_logger, mock_webdriver):
        mock_driver_instance = MagicMock()
        mock_driver_instance.find_element.return_value.send_keys.return_value = None
        mock_driver_instance.find_element.return_value.click.return_value = None

        self.connection = MudfishConnection(web_driver=mock_driver_instance)
        self.connection.login(self.username, self.password, self.adminpage)

        mock_driver_instance.get.assert_called_once_with(self.adminpage)
        mock_driver_instance.find_element.assert_any_call(By.ID, "username")
        mock_driver_instance.find_element.assert_any_call(By.ID, "password")
        mock_driver_instance.find_element.assert_any_call(By.CLASS_NAME, "btn")
        mock_logger.info.assert_any_call("Logging into Mudfish host...")
        mock_logger.info.assert_any_call("Successfully logged into Mudfish")

    @patch('selenium.webdriver.chrome.webdriver.WebDriver')
    @patch('auto_mudfish.connection.logger')
    def test_login_with_driver_webdriver_exception(self, mock_logger, mock_webdriver):
        mock_driver_instance = MagicMock()
        mock_driver_instance.get.side_effect = WebDriverException("Test WebDriver Exception")

        self.connection = MudfishConnection(web_driver=mock_driver_instance)
        self.connection.login(self.username, self.password, self.adminpage)

        mock_logger.exception.assert_called_once()

    @patch('selenium.webdriver.chrome.webdriver.WebDriver')
    @patch('auto_mudfish.connection.WebDriverWait')
    @patch('auto_mudfish.connection.logger')
    def test_get_connect_button_not_found(self, mock_logger, mock_wait, mock_webdriver):
        from selenium.common.exceptions import TimeoutException
        mock_driver_instance = MagicMock()
        mock_wait.return_value.until.side_effect = TimeoutException("Test timeout") # Raise an instance of the exception

        self.connection = MudfishConnection(web_driver=mock_driver_instance)
        result = self.connection.get_connect_button(use_start_condition=True)
        self.assertIsNone(result)
        mock_logger.debug.assert_called_once_with("No `Connect` button found!")

    @patch('selenium.webdriver.chrome.webdriver.WebDriver')
    @patch('auto_mudfish.connection.WebDriverWait')
    @patch('auto_mudfish.connection.logger')
    def test_get_disconnect_button_found(self, mock_logger, mock_wait, mock_webdriver):
        mock_driver_instance = MagicMock()
        mock_button = MagicMock()
        mock_button.is_displayed.return_value = True
        mock_wait.return_value.until.return_value = mock_button

        self.connection = MudfishConnection(web_driver=mock_driver_instance)
        result = self.connection.get_disconnect_button(use_stop_condition=True)
        self.assertEqual(result, mock_button)
        mock_wait.assert_called_once()
        mock_logger.debug.assert_not_called()

    @patch('selenium.webdriver.chrome.webdriver.WebDriver')
    @patch('auto_mudfish.connection.WebDriverWait')
    @patch('auto_mudfish.connection.logger')
    def test_get_disconnect_button_not_found(self, mock_logger, mock_wait, mock_webdriver):
        from selenium.common.exceptions import NoSuchElementException
        mock_driver_instance = MagicMock()
        mock_driver_instance.find_element.side_effect = NoSuchElementException("Test element not found") # Raise an instance of the exception

        self.connection = MudfishConnection(web_driver=mock_driver_instance)
        result = self.connection.get_disconnect_button()
        self.assertIsNone(result)
        mock_logger.debug.assert_called_once_with("No `Disconnect` button found!")

    @patch.object(MudfishConnection, 'get_connect_button')
    @patch.object(MudfishConnection, 'is_mudfish_connected')
    @patch('auto_mudfish.connection.logger')
    def test_connect_success(self, mock_logger, mock_is_connected, mock_get_connect_button):
        mock_driver_instance = MagicMock()
        mock_button = MagicMock()
        mock_get_connect_button.return_value = mock_button
        mock_is_connected.return_value = True

        self.connection = MudfishConnection(web_driver=mock_driver_instance)
        self.connection.connect()

        mock_get_connect_button.assert_called_once()
        mock_button.click.assert_called_once()
        mock_is_connected.assert_called_once()
        mock_logger.info.assert_any_call("Starting Mudfish connection...")
        mock_logger.info.assert_any_call("Mudfish connection started successfully!")

    @patch.object(MudfishConnection, 'get_connect_button')
    @patch.object(MudfishConnection, 'is_mudfish_connected')
    @patch('auto_mudfish.connection.logger')
    def test_connect_already_connected(self, mock_logger, mock_is_connected, mock_get_connect_button):
        mock_get_connect_button.return_value = None  # Simulate no connect button, so already connected

        self.connection = MudfishConnection(web_driver=MagicMock())
        self.connection.connect()

        mock_get_connect_button.assert_called_once()
        mock_is_connected.assert_not_called()
        mock_logger.info.assert_any_call("Mudfish connection is already started!")

    @patch.object(MudfishConnection, 'get_connect_button')
    @patch.object(MudfishConnection, 'is_mudfish_connected')
    @patch('auto_mudfish.connection.logger')
    def test_connect_failed_to_start(self, mock_logger, mock_is_connected, mock_get_connect_button):
        mock_driver_instance = MagicMock()
        mock_button = MagicMock()
        mock_get_connect_button.return_value = mock_button
        mock_is_connected.return_value = False  # Connection fails to start

        self.connection = MudfishConnection(web_driver=mock_driver_instance)
        self.connection.connect()

        mock_get_connect_button.assert_called_once()
        mock_button.click.assert_called_once()
        mock_is_connected.assert_called_once()
        mock_logger.error.assert_called_once_with("Mudfish connection could not be started!")

    @patch.object(MudfishConnection, 'get_disconnect_button')
    @patch.object(MudfishConnection, 'is_mudfish_disconnected')
    @patch('auto_mudfish.connection.logger')
    def test_disconnect_success(self, mock_logger, mock_is_disconnected, mock_get_disconnect_button):
        mock_driver_instance = MagicMock()
        mock_button = MagicMock()
        mock_get_disconnect_button.return_value = mock_button
        mock_is_disconnected.return_value = True

        self.connection = MudfishConnection(web_driver=mock_driver_instance)
        self.connection.disconnect()

        mock_get_disconnect_button.assert_called_once()
        mock_button.click.assert_called_once()
        mock_is_disconnected.assert_called_once()
        mock_logger.info.assert_any_call("Stopping Mudfish connection...")
        mock_logger.info.assert_any_call("Mudfish connection stopped successfully!")

    @patch.object(MudfishConnection, 'get_disconnect_button')
    @patch.object(MudfishConnection, 'is_mudfish_disconnected')
    @patch('auto_mudfish.connection.logger')
    def test_disconnect_already_disconnected(self, mock_logger, mock_is_disconnected, mock_get_disconnect_button):
        mock_get_disconnect_button.return_value = None  # Simulate no disconnect button, so already disconnected

        self.connection = MudfishConnection(web_driver=MagicMock())
        self.connection.disconnect()

        mock_get_disconnect_button.assert_called_once()
        mock_is_disconnected.assert_not_called()
        mock_logger.info.assert_any_call("Mudfish connection is already stopped!")

    @patch.object(MudfishConnection, 'get_disconnect_button')
    @patch.object(MudfishConnection, 'is_mudfish_disconnected')
    @patch('auto_mudfish.connection.logger')
    def test_disconnect_failed_to_stop(self, mock_logger, mock_is_disconnected, mock_get_disconnect_button):
        mock_driver_instance = MagicMock()
        mock_button = MagicMock()
        mock_get_disconnect_button.return_value = mock_button
        mock_is_disconnected.return_value = False  # Disconnection fails to stop

        self.connection = MudfishConnection(web_driver=mock_driver_instance)
        self.connection.disconnect()

        mock_get_disconnect_button.assert_called_once()
        mock_button.click.assert_called_once()
        mock_is_disconnected.assert_called_once()
        mock_logger.error.assert_called_once_with("Mudfish connection could not be stopped!")

    @patch.object(MudfishConnection, 'get_disconnect_button')
    def test_is_mudfish_connected_true(self, mock_get_disconnect_button):
        mock_get_disconnect_button.return_value = MagicMock()  # Button found means connected
        self.connection = MudfishConnection(web_driver=MagicMock())
        self.assertTrue(self.connection.is_mudfish_connected())

    @patch.object(MudfishConnection, 'get_disconnect_button')
    def test_is_mudfish_connected_false(self, mock_get_disconnect_button):
        mock_get_disconnect_button.return_value = None  # No button found means not connected
        self.connection = MudfishConnection(web_driver=MagicMock())
        self.assertFalse(self.connection.is_mudfish_connected())

    @patch.object(MudfishConnection, 'get_connect_button')
    def test_is_mudfish_disconnected_true(self, mock_get_connect_button):
        mock_get_connect_button.return_value = MagicMock()  # Button found means disconnected
        self.connection = MudfishConnection(web_driver=MagicMock())
        self.assertTrue(self.connection.is_mudfish_disconnected())

    @patch.object(MudfishConnection, 'get_connect_button')
    def test_is_mudfish_disconnected_false(self, mock_get_connect_button):
        mock_get_connect_button.return_value = None  # No button found means not disconnected
        self.connection = MudfishConnection(web_driver=MagicMock())
        self.assertFalse(self.connection.is_mudfish_disconnected())
