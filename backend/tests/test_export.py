"""
Tests for export functionality (CSV and JSON export of custody events).

Tests AUDIT-001: Export complete audit logs as CSV/JSON for incident response
and compliance requests.
"""

import pytest
import json
import csv
from io import StringIO
from datetime import datetime, timedelta
from app.models.user import User
from app.models.kit import Kit, KitStatus
from app.models.custody_event import CustodyEvent, CustodyEventType


def test_export_csv_success(client, db_session):
    """Test successful CSV export of custody events"""
    # Create admin user
    admin = User(
        email="admin@example.com",
        name="Test Admin",
        oauth_provider="google",
        oauth_id="test-admin-id",
        role="admin",
        is_active=True
    )
    db_session.add(admin)
    
    # Create coach user
    coach = User(
        email="coach@example.com",
        name="Test Coach",
        oauth_provider="google",
        oauth_id="test-coach-id",
        role="coach",
        is_active=True
    )
    db_session.add(coach)
    
    # Create kit
    kit = Kit(
        code="KIT001",
        name="Test Kit",
        description="Test kit for export",
        status=KitStatus.checked_out
    )
    db_session.add(kit)
    db_session.commit()
    
    # Create custody events
    event1 = CustodyEvent(
        event_type=CustodyEventType.checkout_onprem,
        kit_id=kit.id,
        initiated_by_id=coach.id,
        initiated_by_name=coach.name,
        custodian_id=None,
        custodian_name="John Doe",
        notes="Test checkout",
        location_type="on_premises"
    )
    db_session.add(event1)
    
    event2 = CustodyEvent(
        event_type=CustodyEventType.checkin,
        kit_id=kit.id,
        initiated_by_id=coach.id,
        initiated_by_name=coach.name,
        custodian_id=coach.id,
        custodian_name=coach.name,
        notes="Test checkin",
        location_type="on_premises"
    )
    db_session.add(event2)
    db_session.commit()
    
    # Call export endpoint
    response = client.get("/api/v1/custody/export?format=csv")
    
    # Verify response
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"
    assert "attachment; filename=" in response.headers.get("content-disposition", "")
    
    # Parse CSV and verify content
    csv_content = StringIO(response.text)
    reader = csv.DictReader(csv_content)
    rows = list(reader)
    
    assert len(rows) == 2
    assert rows[0]["event_type"] == "checkout_onprem"
    assert rows[0]["custodian_name"] == "John Doe"
    assert rows[0]["notes"] == "Test checkout"
    assert rows[1]["event_type"] == "checkin"
    assert rows[1]["custodian_name"] == coach.name


def test_export_json_success(client, db_session):
    """Test successful JSON export of custody events"""
    # Create admin user
    admin = User(
        email="admin@example.com",
        name="Test Admin",
        oauth_provider="google",
        oauth_id="test-admin-id",
        role="admin",
        is_active=True
    )
    db_session.add(admin)
    
    # Create coach user
    coach = User(
        email="coach@example.com",
        name="Test Coach",
        oauth_provider="google",
        oauth_id="test-coach-id",
        role="coach",
        is_active=True
    )
    db_session.add(coach)
    
    # Create kit
    kit = Kit(
        code="KIT001",
        name="Test Kit",
        description="Test kit for export",
        status=KitStatus.checked_out
    )
    db_session.add(kit)
    db_session.commit()
    
    # Create custody event
    event = CustodyEvent(
        event_type=CustodyEventType.checkout_offsite,
        kit_id=kit.id,
        initiated_by_id=coach.id,
        initiated_by_name=coach.name,
        custodian_id=None,
        custodian_name="Jane Smith",
        notes="Offsite test",
        location_type="off_site"
    )
    db_session.add(event)
    db_session.commit()
    
    # Call export endpoint
    response = client.get("/api/v1/custody/export?format=json")
    
    # Verify response
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    assert "attachment; filename=" in response.headers.get("content-disposition", "")
    
    # Parse JSON and verify content
    data = json.loads(response.text)
    
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["event_type"] == "checkout_offsite"
    assert data[0]["custodian_name"] == "Jane Smith"
    assert data[0]["notes"] == "Offsite test"
    assert data[0]["location_type"] == "off_site"


def test_export_with_date_filtering(client, db_session):
    """Test export with date range filtering"""
    # Create admin user
    admin = User(
        email="admin@example.com",
        name="Test Admin",
        oauth_provider="google",
        oauth_id="test-admin-id",
        role="admin",
        is_active=True
    )
    db_session.add(admin)
    
    # Create coach user
    coach = User(
        email="coach@example.com",
        name="Test Coach",
        oauth_provider="google",
        oauth_id="test-coach-id",
        role="coach",
        is_active=True
    )
    db_session.add(coach)
    
    # Create kit
    kit = Kit(
        code="KIT001",
        name="Test Kit",
        description="Test kit for export",
        status=KitStatus.available
    )
    db_session.add(kit)
    db_session.commit()
    
    # Create events with different timestamps
    now = datetime.now()
    old_event = CustodyEvent(
        event_type=CustodyEventType.checkout_onprem,
        kit_id=kit.id,
        initiated_by_id=coach.id,
        initiated_by_name=coach.name,
        custodian_id=None,
        custodian_name="Old User",
        notes="Old event",
        location_type="on_premises",
        created_at=now - timedelta(days=30)
    )
    db_session.add(old_event)
    
    recent_event = CustodyEvent(
        event_type=CustodyEventType.checkout_onprem,
        kit_id=kit.id,
        initiated_by_id=coach.id,
        initiated_by_name=coach.name,
        custodian_id=None,
        custodian_name="Recent User",
        notes="Recent event",
        location_type="on_premises",
        created_at=now - timedelta(days=5)
    )
    db_session.add(recent_event)
    db_session.commit()
    
    # Export with date filter - only recent events
    start_date = (now - timedelta(days=10)).isoformat()
    response = client.get(f"/api/v1/custody/export?format=json&start_date={start_date}")
    
    # Verify response
    assert response.status_code == 200
    data = json.loads(response.text)
    
    # Should only include recent event
    assert len(data) == 1
    assert data[0]["custodian_name"] == "Recent User"


def test_export_requires_admin(client, db_session):
    """Test that export endpoint requires admin role"""
    # Create non-admin user (coach)
    coach = User(
        email="coach@example.com",
        name="Test Coach",
        oauth_provider="google",
        oauth_id="test-coach-id",
        role="coach",
        is_active=True
    )
    db_session.add(coach)
    db_session.commit()
    
    # Try to export (should fail - coach not admin)
    response = client.get("/api/v1/custody/export?format=csv")
    
    # Verify access denied
    assert response.status_code == 403
    assert "Only admins can export audit logs" in response.json()["detail"]


def test_export_invalid_format(client, db_session):
    """Test export with invalid format parameter"""
    # Create admin user
    admin = User(
        email="admin@example.com",
        name="Test Admin",
        oauth_provider="google",
        oauth_id="test-admin-id",
        role="admin",
        is_active=True
    )
    db_session.add(admin)
    db_session.commit()
    
    # Create coach to satisfy mock auth
    coach = User(
        email="coach@example.com",
        name="Test Coach",
        oauth_provider="google",
        oauth_id="test-coach-id",
        role="coach",
        is_active=True
    )
    db_session.add(coach)
    db_session.commit()
    
    # Try to export with invalid format
    response = client.get("/api/v1/custody/export?format=xml")
    
    # Verify error
    assert response.status_code == 400
    assert "Invalid format" in response.json()["detail"]


def test_export_invalid_date_format(client, db_session):
    """Test export with invalid date format"""
    # Create admin user
    admin = User(
        email="admin@example.com",
        name="Test Admin",
        oauth_provider="google",
        oauth_id="test-admin-id",
        role="admin",
        is_active=True
    )
    db_session.add(admin)
    db_session.commit()
    
    # Create coach to satisfy mock auth
    coach = User(
        email="coach@example.com",
        name="Test Coach",
        oauth_provider="google",
        oauth_id="test-coach-id",
        role="coach",
        is_active=True
    )
    db_session.add(coach)
    db_session.commit()
    
    # Try to export with invalid date
    response = client.get("/api/v1/custody/export?format=csv&start_date=invalid-date")
    
    # Verify error
    assert response.status_code == 400
    assert "Invalid start_date format" in response.json()["detail"]


def test_export_invalid_date_range(client, db_session):
    """Test export with start_date after end_date"""
    # Create admin user
    admin = User(
        email="admin@example.com",
        name="Test Admin",
        oauth_provider="google",
        oauth_id="test-admin-id",
        role="admin",
        is_active=True
    )
    db_session.add(admin)
    db_session.commit()
    
    # Create coach to satisfy mock auth
    coach = User(
        email="coach@example.com",
        name="Test Coach",
        oauth_provider="google",
        oauth_id="test-coach-id",
        role="coach",
        is_active=True
    )
    db_session.add(coach)
    db_session.commit()
    
    # Try to export with invalid date range
    start = "2024-12-31T23:59:59"
    end = "2024-01-01T00:00:00"
    response = client.get(f"/api/v1/custody/export?format=csv&start_date={start}&end_date={end}")
    
    # Verify error
    assert response.status_code == 400
    assert "start_date must be before end_date" in response.json()["detail"]


def test_export_empty_results(client, db_session):
    """Test export when no events exist"""
    # Create admin user
    admin = User(
        email="admin@example.com",
        name="Test Admin",
        oauth_provider="google",
        oauth_id="test-admin-id",
        role="admin",
        is_active=True
    )
    db_session.add(admin)
    db_session.commit()
    
    # Create coach to satisfy mock auth
    coach = User(
        email="coach@example.com",
        name="Test Coach",
        oauth_provider="google",
        oauth_id="test-coach-id",
        role="coach",
        is_active=True
    )
    db_session.add(coach)
    db_session.commit()
    
    # Export when no events exist
    response = client.get("/api/v1/custody/export?format=csv")
    
    # Verify response (should succeed but be empty)
    assert response.status_code == 200
    
    # Parse CSV and verify it only has headers
    csv_content = StringIO(response.text)
    reader = csv.DictReader(csv_content)
    rows = list(reader)
    assert len(rows) == 0
