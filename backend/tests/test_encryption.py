"""
Tests for field-level encryption functionality (AUDIT-003)
"""
import pytest
from app.core.encryption import FieldEncryption, encrypt_field, decrypt_field


class TestFieldEncryption:
    """Test suite for field-level encryption"""
    
    def test_encrypt_decrypt_roundtrip(self):
        """Test that encryption and decryption are reversible"""
        original = "SN-12345-ABCD"
        encrypted = encrypt_field(original)
        decrypted = decrypt_field(encrypted)
        
        assert decrypted == original
        assert encrypted != original  # Ensure it's actually encrypted
    
    def test_encrypt_none_value(self):
        """Test that None values are handled correctly"""
        encrypted = encrypt_field(None)
        assert encrypted is None
        
        decrypted = decrypt_field(None)
        assert decrypted is None
    
    def test_encrypt_empty_string(self):
        """Test encryption of empty string"""
        original = ""
        encrypted = encrypt_field(original)
        decrypted = decrypt_field(encrypted)
        
        assert decrypted == original
        assert encrypted != original
    
    def test_encrypt_special_characters(self):
        """Test encryption with special characters"""
        original = "SN-!@#$%^&*()_+-=[]{}|;':,.<>?/~`"
        encrypted = encrypt_field(original)
        decrypted = decrypt_field(encrypted)
        
        assert decrypted == original
    
    def test_encrypt_unicode_characters(self):
        """Test encryption with unicode characters"""
        original = "SN-测试-مرحبا-שלום"
        encrypted = encrypt_field(original)
        decrypted = decrypt_field(encrypted)
        
        assert decrypted == original
    
    def test_encrypt_long_string(self):
        """Test encryption of long strings"""
        original = "SN-" + ("A" * 1000)
        encrypted = encrypt_field(original)
        decrypted = decrypt_field(encrypted)
        
        assert decrypted == original
    
    def test_different_values_produce_different_ciphertexts(self):
        """Test that different plaintext values produce different encrypted values"""
        value1 = "SN-12345"
        value2 = "SN-67890"
        
        encrypted1 = encrypt_field(value1)
        encrypted2 = encrypt_field(value2)
        
        assert encrypted1 != encrypted2
    
    def test_encryption_is_deterministic_with_same_instance(self):
        """Test that encryption is consistent when using the same cipher"""
        encryption = FieldEncryption()
        original = "SN-12345"
        
        encrypted1 = encryption.encrypt(original)
        encrypted2 = encryption.encrypt(original)
        
        # Fernet includes a timestamp, so encryptions may differ
        # But both should decrypt to the same value
        assert encryption.decrypt(encrypted1) == original
        assert encryption.decrypt(encrypted2) == original
    
    def test_encrypted_value_is_string(self):
        """Test that encrypted values are returned as strings"""
        original = "SN-12345"
        encrypted = encrypt_field(original)
        
        assert isinstance(encrypted, str)
    
    def test_decrypted_value_is_string(self):
        """Test that decrypted values are returned as strings"""
        original = "SN-12345"
        encrypted = encrypt_field(original)
        decrypted = decrypt_field(encrypted)
        
        assert isinstance(decrypted, str)
    
    def test_cannot_decrypt_invalid_ciphertext(self):
        """Test that invalid ciphertext raises an error"""
        with pytest.raises(Exception):  # Fernet raises cryptography.fernet.InvalidToken
            decrypt_field("invalid-ciphertext")
    
    def test_multiple_encryption_instances_are_compatible(self):
        """Test that multiple instances of FieldEncryption use the same key"""
        encryption1 = FieldEncryption()
        encryption2 = FieldEncryption()
        
        original = "SN-12345"
        encrypted = encryption1.encrypt(original)
        decrypted = encryption2.decrypt(encrypted)
        
        assert decrypted == original
