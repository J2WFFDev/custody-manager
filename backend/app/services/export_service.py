"""
Service for exporting audit logs (custody events) to CSV and JSON formats.

Implements AUDIT-001: Export complete audit logs as CSV/JSON for incident response
and compliance requests.
"""

import csv
import json
from io import StringIO
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.custody_event import CustodyEvent


def export_custody_events_to_csv(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> str:
    """
    Export custody events to CSV format.
    
    Args:
        db: Database session
        start_date: Optional start date for filtering
        end_date: Optional end date for filtering
        
    Returns:
        CSV string with all custody events
    """
    # Build query
    query = db.query(CustodyEvent)
    
    # Apply date filtering if provided
    if start_date:
        query = query.filter(CustodyEvent.created_at >= start_date)
    if end_date:
        query = query.filter(CustodyEvent.created_at <= end_date)
    
    # Order by creation date
    query = query.order_by(CustodyEvent.created_at.asc())
    
    # Fetch events
    events = query.all()
    
    # Create CSV
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'id',
        'event_type',
        'kit_id',
        'initiated_by_id',
        'initiated_by_name',
        'custodian_id',
        'custodian_name',
        'notes',
        'location_type',
        'created_at',
        'updated_at'
    ])
    
    # Write data rows
    for event in events:
        writer.writerow([
            event.id,
            event.event_type.value,
            event.kit_id,
            event.initiated_by_id,
            event.initiated_by_name,
            event.custodian_id or '',
            event.custodian_name,
            event.notes or '',
            event.location_type,
            event.created_at.isoformat(),
            event.updated_at.isoformat()
        ])
    
    return output.getvalue()


def export_custody_events_to_json(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> str:
    """
    Export custody events to JSON format.
    
    Args:
        db: Database session
        start_date: Optional start date for filtering
        end_date: Optional end date for filtering
        
    Returns:
        JSON string with all custody events
    """
    # Build query
    query = db.query(CustodyEvent)
    
    # Apply date filtering if provided
    if start_date:
        query = query.filter(CustodyEvent.created_at >= start_date)
    if end_date:
        query = query.filter(CustodyEvent.created_at <= end_date)
    
    # Order by creation date
    query = query.order_by(CustodyEvent.created_at.asc())
    
    # Fetch events
    events = query.all()
    
    # Convert to list of dicts
    events_data = []
    for event in events:
        events_data.append({
            'id': event.id,
            'event_type': event.event_type.value,
            'kit_id': event.kit_id,
            'initiated_by_id': event.initiated_by_id,
            'initiated_by_name': event.initiated_by_name,
            'custodian_id': event.custodian_id,
            'custodian_name': event.custodian_name,
            'notes': event.notes,
            'location_type': event.location_type,
            'created_at': event.created_at.isoformat(),
            'updated_at': event.updated_at.isoformat()
        })
    
    return json.dumps(events_data, indent=2)
