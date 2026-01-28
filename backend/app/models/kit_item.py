from sqlalchemy import Column, String, Integer, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from app.models.base import BaseModel
from app.core.encryption import encrypt_field, decrypt_field
import enum


class KitItemStatus(str, enum.Enum):
    """Kit item status enum - tracks individual component status"""
    in_kit = "in_kit"
    checked_out = "checked_out"
    lost = "lost"
    maintenance = "maintenance"


class KitItem(BaseModel):
    """
    Kit Item model representing individual components within a kit.
    
    A kit can contain multiple items such as:
    - Firearm (rifle, pistol, etc.)
    - Optic/Sight
    - Case
    - Magazines
    - Tools
    - Other accessories
    
    Each item can have its own attributes and serial number, enabling
    granular tracking, swapping, and compliance management.
    """
    __tablename__ = "kit_items"
    
    # Reference to parent kit
    kit_id = Column(Integer, ForeignKey("kits.id"), nullable=False, index=True)
    
    # Item type (firearm, optic, case, magazine, tool, etc.)
    item_type = Column(String(50), nullable=False, index=True)
    
    # Manufacturer and model information
    make = Column(String(100), nullable=True)
    model = Column(String(100), nullable=True)
    
    # Encrypted serial number field (nullable for items without serials)
    # Stored encrypted in database, transparent to application
    _serial_number_encrypted = Column("serial_number_encrypted", String(500), nullable=True)
    
    # User-friendly name for easy identification
    friendly_name = Column(String(200), nullable=True)
    
    # Photo URL for visual reference
    photo_url = Column(String(500), nullable=True)
    
    # Quantity (useful for magazines, accessories)
    quantity = Column(Integer, nullable=True, default=1)
    
    # Item status
    status = Column(SQLEnum(KitItemStatus), default=KitItemStatus.in_kit, nullable=False)
    
    # Additional notes
    notes = Column(Text, nullable=True)
    
    # Relationship to parent kit
    kit = relationship("Kit", back_populates="items")
    
    def __init__(self, **kwargs):
        # Extract serial_number from kwargs if present  
        has_serial_number = 'serial_number' in kwargs
        serial_number = kwargs.pop('serial_number', None)
        
        # Call parent init with remaining kwargs
        super().__init__(**kwargs)
        
        # Set serial_number using the property setter (which encrypts it)
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
