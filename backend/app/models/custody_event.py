from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class CustodyEvent(Base):
    __tablename__ = "custody_events"
    
    id = Column(Integer, primary_key=True, index=True)
    kit_id = Column(Integer, ForeignKey('kits.id'), nullable=False, index=True)
    event_type = Column(String(50), nullable=False, index=True)
    from_user_id = Column(Integer, ForeignKey('users.id'), index=True)
    to_user_id = Column(Integer, ForeignKey('users.id'), index=True)
    approved_by_user_id = Column(Integer, ForeignKey('users.id'))
    location = Column(String(255))
    attestation_text = Column(Text)
    attestation_signature = Column(Text)
    notes = Column(Text)
    expected_return_date = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    kit = relationship("Kit", foreign_keys=[kit_id])
    from_user = relationship("User", foreign_keys=[from_user_id])
    to_user = relationship("User", foreign_keys=[to_user_id])
    approved_by = relationship("User", foreign_keys=[approved_by_user_id])
    
    def __repr__(self):
        return f"<CustodyEvent {self.event_type} - Kit {self.kit_id}>"
