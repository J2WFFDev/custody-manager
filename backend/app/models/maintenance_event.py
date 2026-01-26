from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class MaintenanceEvent(Base):
    __tablename__ = "maintenance_events"
    
    id = Column(Integer, primary_key=True, index=True)
    kit_id = Column(Integer, ForeignKey('kits.id'), nullable=False, index=True)
    event_type = Column(String(50), nullable=False, index=True)
    performed_by_user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    round_count = Column(Integer)
    parts_replaced = Column(Text)
    notes = Column(Text)
    next_maintenance_date = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    kit = relationship("Kit", foreign_keys=[kit_id])
    performed_by = relationship("User", foreign_keys=[performed_by_user_id])
    
    def __repr__(self):
        return f"<MaintenanceEvent {self.event_type} - Kit {self.kit_id}>"
