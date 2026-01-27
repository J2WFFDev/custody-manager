from sqlalchemy import Column, String, Integer, Enum as SQLEnum
from sqlalchemy.ext.hybrid import hybrid_property
from app.models.base import BaseModel
from app.core.encryption import encrypt_field, decrypt_field
import enum

class KitStatus(str, enum.Enum):
    """Kit status enum - shared between models and schemas"""
    available = "available"
    checked_out = "checked_out"
    in_maintenance = "in_maintenance"
    lost = "lost"

class Kit(BaseModel):
    __tablename__ = "kits"
    
    # Kit code (unique alphanumeric identifier, not exposing serial numbers per QR-004)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(String(500))
    status = Column(SQLEnum(KitStatus), default=KitStatus.available, nullable=False)
    current_custodian_id = Column(Integer, nullable=True)  # Will be FK to User when User model exists
    current_custodian_name = Column(String(200), nullable=True)  # Temporary field until User model exists
    
    # Encrypted serial number field (AUDIT-003)
    # Stored encrypted in database, transparent to application
    _serial_number_encrypted = Column("serial_number_encrypted", String(500), nullable=True)
    
    def __init__(self, **kwargs):
        # Extract serial_number from kwargs if present  
        # Track if it was explicitly provided (could be None or empty string)
        has_serial_number = 'serial_number' in kwargs
        serial_number = kwargs.pop('serial_number', None)
        
        # Call parent init with remaining kwargs
        super().__init__(**kwargs)
        
        # Set serial_number using the property setter (which encrypts it)
        # Only set if it was explicitly provided in kwargs
        if has_serial_number:
            self.serial_number = serial_number
    
    @hybrid_property
    def serial_number(self):
        """Decrypt serial number when accessed."""
        return decrypt_field(self._serial_number_encrypted)
    
    @serial_number.setter
    def serial_number(self, value):
        """Encrypt serial number when set."""
        self._serial_number_encrypted = encrypt_field(value)

