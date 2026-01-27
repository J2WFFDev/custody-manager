"""
Field-level encryption utilities for sensitive data.

This module implements AES-256 encryption for database fields to protect
sensitive information like serial numbers (AUDIT-003).
"""
from typing import Optional
from sqlalchemy import TypeDecorator, String
from cryptography.fernet import Fernet
from app.config import settings
import base64
import hashlib


def get_fernet_key() -> bytes:
    """
    Derive a valid Fernet key from the encryption key in settings.
    
    Fernet requires a 32-byte URL-safe base64-encoded key.
    This function ensures the key from settings is converted to the proper format.
    """
    # Use the encryption key from settings
    key_material = settings.ENCRYPTION_KEY.encode()
    
    # Derive a 32-byte key using SHA-256
    derived_key = hashlib.sha256(key_material).digest()
    
    # Encode as base64 for Fernet
    fernet_key = base64.urlsafe_b64encode(derived_key)
    
    return fernet_key


class EncryptedString(TypeDecorator):
    """
    SQLAlchemy custom type for encrypted string fields.
    
    This type automatically encrypts data before storing in the database
    and decrypts it when reading from the database.
    
    Uses AES-256 encryption via the Fernet symmetric encryption scheme.
    """
    impl = String
    cache_ok = True
    
    def __init__(self, length: Optional[int] = None):
        """
        Initialize the encrypted string type.
        
        Args:
            length: Maximum length of the encrypted field in database.
                   Should be larger than plaintext to account for encryption overhead.
        """
        super().__init__(length=length)
        self._fernet = None
    
    @property
    def fernet(self) -> Fernet:
        """Lazy initialization of Fernet cipher."""
        if self._fernet is None:
            self._fernet = Fernet(get_fernet_key())
        return self._fernet
    
    def process_bind_param(self, value: Optional[str], dialect) -> Optional[str]:
        """
        Encrypt value before storing in database.
        
        Args:
            value: Plain text value to encrypt
            dialect: SQLAlchemy dialect (not used)
            
        Returns:
            Encrypted string or None if value is None
        """
        if value is None:
            return None
        
        # Encrypt the value
        encrypted_bytes = self.fernet.encrypt(value.encode())
        
        # Return as string for database storage
        return encrypted_bytes.decode()
    
    def process_result_value(self, value: Optional[str], dialect) -> Optional[str]:
        """
        Decrypt value when reading from database.
        
        Args:
            value: Encrypted value from database
            dialect: SQLAlchemy dialect (not used)
            
        Returns:
            Decrypted string or None if value is None
        """
        if value is None:
            return None
        
        # Decrypt the value
        decrypted_bytes = self.fernet.decrypt(value.encode())
        
        # Return as string
        return decrypted_bytes.decode()
