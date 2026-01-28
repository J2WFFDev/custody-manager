from sqlalchemy import Column, String, Integer, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from app.models.base import BaseModel
from app.core.encryption import encrypt_field, decrypt_field
import enum


class ItemStatus(str, enum.Enum):
    """Item status enum - tracks item availability and assignment status"""
    available = "available"        # Not assigned to any kit
    assigned = "assigned"          # Assigned to a kit (in storage)
    checked_out = "checked_out"    # Currently checked out with kit
    lost = "lost"                  # Reported lost
    maintenance = "maintenance"    # Under maintenance


class ItemType(str, enum.Enum):
    """Item type enum - categorizes inventory items"""
    firearm = "firearm"
    optic = "optic"
    case = "case"
    magazine = "magazine"
    tool = "tool"
    accessory = "accessory"
    other = "other"


# Keep backward compatibility alias
class KitItemStatus(str, enum.Enum):
    """Deprecated: Use ItemStatus instead"""
    in_kit = "in_kit"
    checked_out = "checked_out"
    lost = "lost"
    maintenance = "maintenance"


class Item(BaseModel):
    """
    Item model representing individual inventory components.
    
    Items are independent inventory objects that can exist with or without kit assignment.
    This enables:
    - Master inventory tracking
    - Item reassignment between kits
    - Lifecycle tracking across multiple kits
    - Unassigned item management
    
    Items can include:
    - Firearms (rifle, pistol, etc.)
    - Optics/Sights
    - Cases
    - Magazines
    - Tools
    - Other accessories
    
    Each item has its own attributes and serial number for granular tracking.
    """
    __tablename__ = "items"
    
    # Reference to current kit (nullable - items can be unassigned)
    current_kit_id = Column(Integer, ForeignKey("kits.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # Item type enum (firearm, optic, case, magazine, tool, etc.)
    item_type = Column(SQLEnum(ItemType), nullable=False, index=True)
    
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
    status = Column(SQLEnum(ItemStatus), default=ItemStatus.available, nullable=False)
    
    # Additional notes
    notes = Column(Text, nullable=True)
    
    # Relationship to current kit (if assigned)
    current_kit = relationship("Kit", back_populates="items", foreign_keys=[current_kit_id])
    
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


# Backward compatibility alias
KitItem = Item
