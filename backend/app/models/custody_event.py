from sqlalchemy import Column, String, Integer, ForeignKey, Enum as SQLEnum
from app.models.base import BaseModel
import enum

class CustodyEventType(str, enum.Enum):
    """Custody event types - immutable audit trail"""
    checkout_onprem = "checkout_onprem"
    checkout_offsite = "checkout_offsite"
    checkin = "checkin"
    transfer = "transfer"
    lost = "lost"
    found = "found"

class CustodyEvent(BaseModel):
    __tablename__ = "custody_events"
    
    # Event type
    event_type = Column(SQLEnum(CustodyEventType), nullable=False)
    
    # Kit reference
    kit_id = Column(Integer, ForeignKey("kits.id"), nullable=False, index=True)
    
    # User who initiated the action (e.g., Coach checking out kit)
    initiated_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    initiated_by_name = Column(String(200), nullable=False)
    
    # User who receives custody (e.g., Athlete receiving kit)
    # For on-prem checkout, this could be a name string if athlete is not in system
    custodian_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    custodian_name = Column(String(200), nullable=False)
    
    # Optional notes
    notes = Column(String(1000), nullable=True)
    
    # Location type (on_premises or off_site)
    location_type = Column(String(50), nullable=False, default="on_premises")
