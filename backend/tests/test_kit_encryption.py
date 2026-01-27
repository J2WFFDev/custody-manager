"""
Integration tests for encrypted serial number field in Kit model (AUDIT-003)
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models.kit import Kit, KitStatus


# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_encryption.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database for each test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


class TestKitSerialNumberEncryption:
    """Test suite for Kit model serial number encryption"""
    
    def test_serial_number_is_encrypted_in_database(self, db_session):
        """Test that serial numbers are stored encrypted in the database"""
        # Create a kit with a serial number
        kit = Kit(
            code="TEST-001",
            name="Test Kit",
            description="A test kit",
            serial_number="SN-12345-ABCD"
        )
        
        db_session.add(kit)
        db_session.commit()
        db_session.refresh(kit)
        
        # The encrypted field should not equal the plaintext
        assert kit._serial_number_encrypted is not None
        assert kit._serial_number_encrypted != "SN-12345-ABCD"
        
        # The hybrid property should return the decrypted value
        assert kit.serial_number == "SN-12345-ABCD"
    
    def test_serial_number_decrypts_on_retrieval(self, db_session):
        """Test that serial numbers are automatically decrypted when retrieved"""
        # Create and save a kit
        kit = Kit(
            code="TEST-002",
            name="Test Kit 2",
            serial_number="SN-67890-XYZ"
        )
        db_session.add(kit)
        db_session.commit()
        kit_id = kit.id
        
        # Clear the session to force a fresh fetch from database
        db_session.expunge_all()
        
        # Retrieve the kit
        retrieved_kit = db_session.query(Kit).filter(Kit.id == kit_id).first()
        
        # Serial number should be decrypted automatically
        assert retrieved_kit.serial_number == "SN-67890-XYZ"
    
    def test_serial_number_can_be_none(self, db_session):
        """Test that serial number can be None (optional field)"""
        kit = Kit(
            code="TEST-003",
            name="Test Kit 3",
            description="Kit without serial number",
            serial_number=None
        )
        
        db_session.add(kit)
        db_session.commit()
        db_session.refresh(kit)
        
        assert kit.serial_number is None
        assert kit._serial_number_encrypted is None
    
    def test_serial_number_can_be_updated(self, db_session):
        """Test that serial numbers can be updated"""
        # Create a kit
        kit = Kit(
            code="TEST-004",
            name="Test Kit 4",
            serial_number="SN-ORIGINAL"
        )
        db_session.add(kit)
        db_session.commit()
        
        # Update the serial number
        kit.serial_number = "SN-UPDATED"
        db_session.commit()
        db_session.refresh(kit)
        
        # Verify the update
        assert kit.serial_number == "SN-UPDATED"
        
        # Encrypted value should have changed
        assert kit._serial_number_encrypted is not None
        assert kit._serial_number_encrypted != "SN-UPDATED"
    
    def test_serial_number_with_special_characters(self, db_session):
        """Test that serial numbers with special characters are handled correctly"""
        special_serial = "SN-!@#$%^&*()_+-=[]{}|;':,.<>?/"
        
        kit = Kit(
            code="TEST-005",
            name="Test Kit 5",
            serial_number=special_serial
        )
        
        db_session.add(kit)
        db_session.commit()
        db_session.refresh(kit)
        
        assert kit.serial_number == special_serial
    
    def test_multiple_kits_with_different_serial_numbers(self, db_session):
        """Test that multiple kits can have different encrypted serial numbers"""
        kit1 = Kit(code="TEST-006", name="Kit 1", serial_number="SN-AAA")
        kit2 = Kit(code="TEST-007", name="Kit 2", serial_number="SN-BBB")
        kit3 = Kit(code="TEST-008", name="Kit 3", serial_number="SN-CCC")
        
        db_session.add_all([kit1, kit2, kit3])
        db_session.commit()
        
        # All encrypted values should be different
        encrypted_values = [
            kit1._serial_number_encrypted,
            kit2._serial_number_encrypted,
            kit3._serial_number_encrypted
        ]
        assert len(set(encrypted_values)) == 3  # All unique
        
        # All decrypted values should match original
        assert kit1.serial_number == "SN-AAA"
        assert kit2.serial_number == "SN-BBB"
        assert kit3.serial_number == "SN-CCC"
    
    def test_query_by_code_returns_decrypted_serial(self, db_session):
        """Test that querying by code returns kit with decrypted serial number"""
        kit = Kit(
            code="QUERY-TEST-001",
            name="Query Test Kit",
            serial_number="SN-QUERY-12345"
        )
        db_session.add(kit)
        db_session.commit()
        
        # Query by code
        found_kit = db_session.query(Kit).filter(Kit.code == "QUERY-TEST-001").first()
        
        assert found_kit is not None
        assert found_kit.serial_number == "SN-QUERY-12345"
    
    def test_serial_number_survives_session_refresh(self, db_session):
        """Test that serial number encryption/decryption works across session operations"""
        kit = Kit(
            code="REFRESH-TEST",
            name="Refresh Test Kit",
            serial_number="SN-REFRESH-999"
        )
        db_session.add(kit)
        db_session.commit()
        
        # Multiple refreshes
        for _ in range(3):
            db_session.refresh(kit)
            assert kit.serial_number == "SN-REFRESH-999"
