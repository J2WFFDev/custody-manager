from sqlalchemy import Column, String, Integer, ForeignKey, Text, Date
from app.models.base import BaseModel

class MaintenanceEvent(BaseModel):
    __tablename__ = "maintenance_events"
    
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
    
    # Next scheduled maintenance date (set when closing maintenance)
    next_maintenance_date = Column(Date, nullable=True)
    
    # Timestamps are inherited from BaseModel (created_at for open, updated_at for close)
