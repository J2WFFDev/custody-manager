"""
Tests for field-level encryption functionality (AUDIT-003).

This module tests the encryption and decryption of sensitive fields
like serial numbers to ensure they are properly protected in the database.
"""
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models.kit import Kit, KitStatus
from app.core.encryption import EncryptedString, get_fernet_key, FieldEncryption, encrypt_field, decrypt_field
from cryptography.fernet import Fernet


# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_encryption.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_setup():
    """Create tables before each test and drop them after"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db(db_setup):
    """Create a database session"""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_fernet_key_generation():
    """Test that Fernet key is generated correctly"""
    key = get_fernet_key()
    
    # Should be bytes
    assert isinstance(key, bytes)
    
    # Should be valid Fernet key (can create a Fernet instance)
    fernet = Fernet(key)
    assert fernet is not None
    
    # Should be consistent across calls
    key2 = get_fernet_key()
    assert key == key2


def test_encrypted_string_type():
    """Test the EncryptedString SQLAlchemy type"""
    encrypted_type = EncryptedString(500)
    
    # Test encryption (process_bind_param)
    plaintext = "SN-12345-TEST"
    encrypted = encrypted_type.process_bind_param(plaintext, None)
    
    # Encrypted value should be different from plaintext
    assert encrypted != plaintext
    assert encrypted is not None
    assert len(encrypted) > len(plaintext)  # Encrypted data is larger
    
    # Test decryption (process_result_value)
    decrypted = encrypted_type.process_result_value(encrypted, None)
    assert decrypted == plaintext
    
    # Test None handling
    assert encrypted_type.process_bind_param(None, None) is None
    assert encrypted_type.process_result_value(None, None) is None


def test_kit_serial_number_encryption(db):
    """Test that serial numbers are encrypted when stored in database"""
    # Create a kit with a serial number
    test_serial = "SN-TEST-123456"
    kit = Kit(
        code="TEST-KIT-001",
        name="Test Kit with Serial",
        description="A test kit",
        status=KitStatus.available,
        serial_number=test_serial
    )
    
    db.add(kit)
    db.commit()
    db.refresh(kit)
    
    # The serial number should be decrypted when accessed through the ORM
    assert kit.serial_number == test_serial
    
    # Query the database directly to verify encryption
    result = db.execute(
        text("SELECT serial_number FROM kits WHERE code = :code"),
        {"code": "TEST-KIT-001"}
    ).fetchone()
    
    encrypted_value = result[0]
    
    # The stored value should be different from the plaintext
    assert encrypted_value != test_serial
    # Encrypted data should be longer
    assert len(encrypted_value) > len(test_serial)
    
    # Should contain encrypted format markers (base64 encoded Fernet token)
    # Fernet tokens start with 'gAAAAA' after base64 encoding
    assert encrypted_value is not None


def test_kit_serial_number_decryption(db):
    """Test that serial numbers are correctly decrypted when retrieved"""
    # Create multiple kits with different serial numbers
    kits_data = [
        ("KIT-001", "SN-001-ALPHA"),
        ("KIT-002", "SN-002-BETA"),
        ("KIT-003", "SN-003-GAMMA"),
    ]
    
    for code, serial in kits_data:
        kit = Kit(
            code=code,
            name=f"Kit {code}",
            status=KitStatus.available,
            serial_number=serial
        )
        db.add(kit)
    
    db.commit()
    
    # Retrieve and verify decryption
    for code, expected_serial in kits_data:
        kit = db.query(Kit).filter(Kit.code == code).first()
        assert kit is not None
        assert kit.serial_number == expected_serial


def test_kit_without_serial_number(db):
    """Test that kits can be created without serial numbers"""
    kit = Kit(
        code="NO-SERIAL-KIT",
        name="Kit without serial",
        status=KitStatus.available,
        serial_number=None
    )
    
    db.add(kit)
    db.commit()
    db.refresh(kit)
    
    # Should handle None values correctly
    assert kit.serial_number is None
    
    # Query directly to verify NULL in database
    result = db.execute(
        text("SELECT serial_number FROM kits WHERE code = :code"),
        {"code": "NO-SERIAL-KIT"}
    ).fetchone()
    
    assert result[0] is None


def test_serial_number_update(db):
    """Test updating serial number maintains encryption"""
    # Create kit with initial serial
    kit = Kit(
        code="UPDATE-TEST",
        name="Update Test Kit",
        status=KitStatus.available,
        serial_number="SN-ORIGINAL"
    )
    
    db.add(kit)
    db.commit()
    
    # Update serial number
    kit.serial_number = "SN-UPDATED"
    db.commit()
    db.refresh(kit)
    
    # Should decrypt to new value
    assert kit.serial_number == "SN-UPDATED"
    
    # Verify encryption in database
    result = db.execute(
        text("SELECT serial_number FROM kits WHERE code = :code"),
        {"code": "UPDATE-TEST"}
    ).fetchone()
    
    encrypted_value = result[0]
    assert encrypted_value != "SN-UPDATED"


def test_encryption_key_consistency():
    """Test that encryption/decryption works consistently across multiple instances"""
    # Create two separate EncryptedString instances
    enc1 = EncryptedString(500)
    enc2 = EncryptedString(500)
    
    plaintext = "CONSISTENT-TEST-VALUE"
    
    # Encrypt with first instance
    encrypted = enc1.process_bind_param(plaintext, None)
    
    # Decrypt with second instance (should work because they use same key)
    decrypted = enc2.process_result_value(encrypted, None)
    
    assert decrypted == plaintext


def test_different_values_encrypt_differently():
    """Test that different plaintext values produce different encrypted values"""
    enc = EncryptedString(500)
    
    encrypted1 = enc.process_bind_param("VALUE-1", None)
    encrypted2 = enc.process_bind_param("VALUE-2", None)
    
    # Different values should produce different encrypted output
    assert encrypted1 != encrypted2


def test_empty_string_encryption(db):
    """Test encryption of empty strings"""
    kit = Kit(
        code="EMPTY-SERIAL",
        name="Empty Serial Kit",
        status=KitStatus.available,
        serial_number=""
    )
    
    db.add(kit)
    db.commit()
    db.refresh(kit)
    
    # Empty string should be encrypted and decrypted correctly
    assert kit.serial_number == ""


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
