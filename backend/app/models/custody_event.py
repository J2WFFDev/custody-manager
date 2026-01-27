from sqlalchemy import Column, String, Integer, ForeignKey, Enum as SQLEnum, Date, Text, DateTime, event
from sqlalchemy.orm import validates
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
    """
    Append-only custody event model for immutable audit trail.
    
    Implements CUSTODY-015: All custody events are append-only and immutable.
    
    This model enforces:
    - No updates allowed (raises exception on update attempt)
    - No deletes allowed (raises exception on delete attempt)
    - All fields are set once at creation time
    
    Fields mapping to requirements:
    - event_type: Type of custody event
    - from_user: initiated_by_id/initiated_by_name
    - to_user: custodian_id/custodian_name
    - approved_by: approved_by_id/approved_by_name
    - attestation: attestation_text, attestation_signature, etc.
    - location: location_type
    - notes: notes
    """
    __tablename__ = "custody_events"
    
    # Event type
    event_type = Column(SQLEnum(CustodyEventType), nullable=False)
    
    # Kit reference
    kit_id = Column(Integer, ForeignKey("kits.id"), nullable=False, index=True)
    
    # User who initiated the action (e.g., Coach checking out kit)
    # This maps to 'from_user' in the requirements
    initiated_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    initiated_by_name = Column(String(200), nullable=False)
    
    # User who receives custody (e.g., Athlete receiving kit)
    # This maps to 'to_user' in the requirements
    # For on-prem checkout, this could be a name string if athlete is not in system
    custodian_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    custodian_name = Column(String(200), nullable=False)
    
    # User who approved the custody event (e.g., Armorer or Coach approving off-site checkout)
    # This maps to 'approved_by' in the requirements
    approved_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_by_name = Column(String(200), nullable=True)
    
    # Optional notes
    notes = Column(String(1000), nullable=True)
    
    # Location type (on_premises or off_site)
    # This maps to 'location' in the requirements
    location_type = Column(String(50), nullable=False, default="on_premises")
    
    # Expected return date (for soft warnings - CUSTODY-008, CUSTODY-014)
    # Optional for on-premises checkouts, recommended for off-site checkouts
    expected_return_date = Column(Date, nullable=True)
    
    # Attestation fields for legal acknowledgment (CUSTODY-012, CUSTODY-015)
    # This maps to 'attestation' in the requirements
    attestation_text = Column(Text, nullable=True)  # The legal text presented to user
    attestation_signature = Column(String(200), nullable=True)  # Digital signature/acknowledgment
    attestation_timestamp = Column(DateTime, nullable=True)  # When user acknowledged
    attestation_ip_address = Column(String(45), nullable=True)  # IP address for audit trail


# Enforce append-only behavior using SQLAlchemy events
@event.listens_for(CustodyEvent, 'before_update')
def prevent_custody_event_update(mapper, connection, target):
    """
    Prevent updates to custody events (CUSTODY-015: append-only enforcement).
    
    This event listener is triggered before any UPDATE operation on the custody_events table.
    It raises an exception to prevent the update, ensuring immutability.
    """
    raise ValueError(
        "Cannot update custody events: Custody events are append-only and "
        "immutable (CUSTODY-015). Create a new event instead."
    )


@event.listens_for(CustodyEvent, 'before_delete')
def prevent_custody_event_delete(mapper, connection, target):
    """
    Prevent deletion of custody events (CUSTODY-015: append-only enforcement).
    
    This event listener is triggered before any DELETE operation on the custody_events table.
    It raises an exception to prevent the deletion, ensuring immutability.
    """
    raise ValueError(
        "Cannot delete custody events: Custody events are append-only and "
        "immutable (CUSTODY-015). They form a permanent audit trail."
    )
