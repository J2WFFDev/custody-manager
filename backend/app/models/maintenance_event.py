from sqlalchemy import Column, String, Integer, ForeignKey, Text, Boolean
from sqlalchemy import Column, String, Integer, ForeignKey, Text, Date
from app.models.base import BaseModel

class MaintenanceEvent(BaseModel):
    """
    Maintenance event model for tracking equipment maintenance.
    
    Implements:
    - MAINT-001: Track equipment maintenance events
    
    A maintenance event tracks when a kit enters and exits maintenance.
    Each event has an "open" state when maintenance begins and a "close" 
    state when maintenance is completed.
    
    Fields:
        id (int): Primary key, auto-generated (inherited from BaseModel)
        kit_id (int): Foreign key to the kit being maintained
        opened_by_id (int): Foreign key to user who opened the maintenance
        opened_by_name (str): Name of user who opened maintenance
        closed_by_id (int): Foreign key to user who closed maintenance (nullable)
        closed_by_name (str): Name of user who closed maintenance (nullable)
        notes (text): Additional notes about the maintenance
        parts_replaced (text): Description of parts replaced
        round_count (int): Number of rounds fired (if applicable)
        is_open (bool): True if maintenance is currently open, False if closed
        created_at (datetime): When maintenance was opened (inherited from BaseModel)
        updated_at (datetime): When maintenance was last updated (inherited from BaseModel)
    """
    __tablename__ = "maintenance_events"
    
    # Kit reference
    kit_id = Column(Integer, ForeignKey("kits.id"), nullable=False, index=True)
    
    # User who opened the maintenance
    opened_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    opened_by_name = Column(String(200), nullable=False)
    
    # User who closed the maintenance (nullable until closed)
    closed_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    closed_by_name = Column(String(200), nullable=True)
    
    # Maintenance details - using Text for potentially long content
    notes = Column(Text, nullable=True)
    parts_replaced = Column(Text, nullable=True)
    round_count = Column(Integer, nullable=True)
    
    # Status tracking - True for open, False for closed
    is_open = Column(Boolean, nullable=False, default=True)
    
    # Next scheduled maintenance date (set when closing maintenance)
    next_maintenance_date = Column(Date, nullable=True)
    
    # Timestamps are inherited from BaseModel (created_at for open, updated_at for close)
