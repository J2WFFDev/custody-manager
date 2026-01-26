from sqlalchemy.orm import Session
from typing import Optional
from app.models.kit import Kit
from app.schemas.kit import KitLookupResponse

class KitService:
    """Service class for kit-related operations"""
    
    @staticmethod
    def lookup_by_code(db: Session, code: str) -> Optional[KitLookupResponse]:
        """
        Lookup a kit by its code (from QR scan or manual entry)
        
        Args:
            db: Database session
            code: Kit code to lookup
            
        Returns:
            KitLookupResponse if found, None otherwise
        """
        kit = db.query(Kit).filter(Kit.code == code).first()
        
        if not kit:
            return None
        
        # Transform to lookup response format
        return KitLookupResponse(
            id=kit.id,
            code=kit.code,
            name=kit.name,
            description=kit.description,
            status=kit.status,
            custodian=kit.current_custodian_name,
            created_at=kit.created_at,
            updated_at=kit.updated_at
        )
