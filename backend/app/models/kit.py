from sqlalchemy import Column, String, Integer, Enum as SQLEnum
from app.models.base import BaseModel
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

