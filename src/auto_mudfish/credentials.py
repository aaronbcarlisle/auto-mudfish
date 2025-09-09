"""
Secure credential management for auto-mudfish.

This module provides encrypted storage and retrieval of Mudfish credentials
using the Windows Data Protection API (DPAPI) for secure local storage.
"""

import os
import json
import base64
import logging
from typing import Optional, Dict, Any
from pathlib import Path

try:
    import win32crypt
    import win32api
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False

logger = logging.getLogger("auto_mudfish.credentials")


class CredentialManager:
    """
    Manages encrypted storage of Mudfish credentials.
    
    Uses Windows DPAPI for secure credential storage. Credentials are encrypted
    using the current user's Windows credentials and stored in a local file.
    """
    
    def __init__(self, credentials_file: Optional[str] = None):
        """
        Initialize the credential manager.
        
        Args:
            credentials_file (Optional[str]): Path to credentials file.
                                            Defaults to ~/.auto_mudfish/credentials.enc
        """
        if credentials_file:
            self.credentials_file = Path(credentials_file)
        else:
            # Use user's home directory for credentials
            home_dir = Path.home()
            credentials_dir = home_dir / ".auto_mudfish"
            credentials_dir.mkdir(exist_ok=True)
            self.credentials_file = credentials_dir / "credentials.enc"
        
        self._ensure_win32_available()
    
    def _ensure_win32_available(self) -> None:
        """Ensure Windows DPAPI is available."""
        if not WIN32_AVAILABLE:
            raise RuntimeError(
                "Windows DPAPI not available. Please ensure pywin32 is installed: "
                "pip install pywin32"
            )
    
    def _encrypt_data(self, data: str) -> bytes:
        """
        Encrypt data using Windows DPAPI.
        
        Args:
            data (str): Data to encrypt.
            
        Returns:
            bytes: Encrypted data.
        """
        try:
            # Convert string to bytes
            data_bytes = data.encode('utf-8')
            # Encrypt using DPAPI - use the correct parameter order
            encrypted = win32crypt.CryptProtectData(
                data_bytes,
                "auto_mudfish_credentials",
                None,  # pOptionalEntropy
                None,  # pvReserved
                None,  # pPromptStruct
                0      # dwFlags
            )
            return encrypted
        except Exception as e:
            logger.error("Failed to encrypt credentials: %s", e)
            raise
    
    def _decrypt_data(self, encrypted_data: bytes) -> str:
        """
        Decrypt data using Windows DPAPI.
        
        Args:
            encrypted_data (bytes): Encrypted data to decrypt.
            
        Returns:
            str: Decrypted data.
        """
        try:
            # Decrypt using DPAPI - use the correct parameter order
            decrypted = win32crypt.CryptUnprotectData(
                encrypted_data,
                None,  # pOptionalEntropy
                None,  # pvReserved
                None,  # pPromptStruct
                0      # dwFlags
            )
            return decrypted[1].decode('utf-8')
        except Exception as e:
            logger.error("Failed to decrypt credentials: %s", e)
            raise
    
    def store_credentials(self, username: str, password: str, adminpage: Optional[str] = None) -> bool:
        """
        Store encrypted credentials.
        
        Args:
            username (str): Mudfish username.
            password (str): Mudfish password.
            adminpage (Optional[str]): Custom admin page URL.
            
        Returns:
            bool: True if credentials were stored successfully.
        """
        try:
            credentials_data = {
                "username": username,
                "password": password,
                "adminpage": adminpage
            }
            
            # Convert to JSON string
            json_data = json.dumps(credentials_data)
            
            # Encrypt the data
            encrypted_data = self._encrypt_data(json_data)
            
            # Encode to base64 for file storage
            encoded_data = base64.b64encode(encrypted_data)
            
            # Write to file
            with open(self.credentials_file, 'wb') as f:
                f.write(encoded_data)
            
            logger.info("Credentials stored successfully")
            return True
            
        except Exception as e:
            logger.error("Failed to store credentials: %s", e)
            return False
    
    def load_credentials(self) -> Optional[Dict[str, Any]]:
        """
        Load and decrypt stored credentials.
        
        Returns:
            Optional[Dict[str, Any]]: Decrypted credentials dict or None if failed.
        """
        try:
            if not self.credentials_file.exists():
                logger.debug("No credentials file found")
                return None
            
            # Read encrypted data
            with open(self.credentials_file, 'rb') as f:
                encoded_data = f.read()
            
            # Decode from base64
            encrypted_data = base64.b64decode(encoded_data)
            
            # Decrypt the data
            decrypted_json = self._decrypt_data(encrypted_data)
            
            # Parse JSON
            credentials = json.loads(decrypted_json)
            
            logger.debug("Credentials loaded successfully")
            return credentials
            
        except Exception as e:
            logger.error("Failed to load credentials: %s", e)
            return None
    
    def clear_credentials(self) -> bool:
        """
        Clear stored credentials.
        
        Returns:
            bool: True if credentials were cleared successfully.
        """
        try:
            if self.credentials_file.exists():
                self.credentials_file.unlink()
                logger.info("Credentials cleared successfully")
            else:
                logger.debug("No credentials file to clear")
            return True
            
        except Exception as e:
            logger.error("Failed to clear credentials: %s", e)
            return False
    
    def has_credentials(self) -> bool:
        """
        Check if credentials are stored.
        
        Returns:
            bool: True if credentials file exists and is readable.
        """
        try:
            if not self.credentials_file.exists():
                return False
            
            # Try to load credentials to verify they're valid
            credentials = self.load_credentials()
            return credentials is not None
            
        except Exception:
            return False
    
    def get_credentials_info(self) -> Optional[Dict[str, str]]:
        """
        Get credential information without the password.
        
        Returns:
            Optional[Dict[str, str]]: Credential info (username, adminpage) or None.
        """
        try:
            credentials = self.load_credentials()
            if credentials:
                return {
                    "username": credentials.get("username", ""),
                    "adminpage": credentials.get("adminpage", ""),
                    "has_password": bool(credentials.get("password"))
                }
            return None
        except Exception as e:
            logger.error("Failed to get credentials info: %s", e)
            return None


def get_credential_manager() -> CredentialManager:
    """
    Get a credential manager instance.
    
    Returns:
        CredentialManager: Configured credential manager instance.
    """
    return CredentialManager()
