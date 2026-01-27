"""
Field-level encryption utility for sensitive database fields.

This module provides encryption/decryption capabilities for sensitive data
such as serial numbers, implementing AUDIT-003 security requirements.
"""
from cryptography.fernet import Fernet
from app.config import settings
import base64
from typing import Optional


class FieldEncryption:
    """
    Handles field-level encryption for sensitive database fields.
    Uses Fernet (symmetric encryption) from the cryptography library.
    """
    
    def __init__(self):
        """Initialize encryption with the configured key."""
        # Ensure the encryption key is properly formatted
        key = settings.ENCRYPTION_KEY.encode() if isinstance(settings.ENCRYPTION_KEY, str) else settings.ENCRYPTION_KEY
        
        # Fernet requires a 32-byte base64-encoded key
        if len(key) != 44:  # base64 encoded 32 bytes = 44 chars
            # Pad or derive key to correct length
            key = base64.urlsafe_b64encode(key.ljust(32, b'\0')[:32])
        
        self._cipher = Fernet(key)
    
    def encrypt(self, plaintext: Optional[str]) -> Optional[str]:
        """
        Encrypt a string value.
        
        Args:
            plaintext: The string to encrypt
            
        Returns:
            Base64-encoded encrypted string, or None if input is None
        """
        if plaintext is None:
            return None
        
        # Convert to bytes, encrypt, and return as string
        encrypted_bytes = self._cipher.encrypt(plaintext.encode('utf-8'))
        return encrypted_bytes.decode('utf-8')
    
    def decrypt(self, ciphertext: Optional[str]) -> Optional[str]:
        """
        Decrypt an encrypted string value.
        
        Args:
            ciphertext: The encrypted string to decrypt
            
        Returns:
            Decrypted plaintext string, or None if input is None
        """
        if ciphertext is None:
            return None
        
        # Convert to bytes, decrypt, and return as string
        decrypted_bytes = self._cipher.decrypt(ciphertext.encode('utf-8'))
        return decrypted_bytes.decode('utf-8')


# Global instance for use throughout the application
field_encryption = FieldEncryption()


def encrypt_field(value: Optional[str]) -> Optional[str]:
    """Convenience function to encrypt a field value."""
    return field_encryption.encrypt(value)


def decrypt_field(value: Optional[str]) -> Optional[str]:
    """Convenience function to decrypt a field value."""
    return field_encryption.decrypt(value)
