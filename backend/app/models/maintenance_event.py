from sqlalchemy import Column, String, Integer, ForeignKey, Date, Enum as SQLEnum
from app.models.base import BaseModel
import enum

class MaintenanceEventType(str, enum.Enum):
    """Maintenance event types"""
    open = "open"
    close = "close"
    parts_replacement = "parts_replacement"
    inspection = "inspection"
    cleaning = "cleaning"
from sqlalchemy import Column, String, Integer, ForeignKey, Text
from app.models.base import BaseModel

class MaintenanceEvent(BaseModel):
    __tablename__ = "maintenance_events"
    
    # Event type
    event_type = Column(SQLEnum(MaintenanceEventType), nullable=False)
    
    # Kit reference
    kit_id = Column(Integer, ForeignKey("kits.id"), nullable=False, index=True)
    
    # User who performed the maintenance (e.g., Armorer)
    performed_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    performed_by_name = Column(String(200), nullable=False)
    
    # Maintenance details
    round_count = Column(Integer, nullable=True)  # Number of rounds fired (if applicable)
    parts_replaced = Column(String(500), nullable=True)  # Description of parts replaced
    notes = Column(String(1000), nullable=True)  # Additional notes
    next_maintenance_date = Column(Date, nullable=True)  # Scheduled next maintenance date
    # Kit reference
    kit_id = Column(Integer, ForeignKey("kits.id"), nullable=False, index=True)
    
    # User who opened the maintenance
    opened_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    opened_by_name = Column(String(200), nullable=False)
    
    # User who closed the maintenance (nullable until closed)
    closed_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    closed_by_name = Column(String(200), nullable=True)
    
    # Maintenance details
    notes = Column(Text, nullable=True)
    parts_replaced = Column(Text, nullable=True)
    round_count = Column(Integer, nullable=True)
    
    # Status tracking - open or closed
    is_open = Column(Integer, nullable=False, default=1)  # 1 for open, 0 for closed
    
    # Timestamps are inherited from BaseModel (created_at for open, updated_at for close)
