"""
Tests for User model and related functionality.

Covers:
- AUTH-001: Role assignment and validation
- AUTH-002: Verified adult flag
- User model CRUD operations
- UserRole enum functionality
"""
import pytest
from sqlalchemy.exc import IntegrityError
from app.models.user import User, UserRole


def test_create_user_with_default_values(db_session):
    """Test creating a user with default values"""
    user = User(
        email="test@example.com",
        name="Test User",
        oauth_provider="google",
        oauth_id="google_123"
    )
    db_session.add(user)
    db_session.commit()
    
    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.name == "Test User"
    assert user.oauth_provider == "google"
    assert user.oauth_id == "google_123"
    assert user.role == UserRole.parent  # Default role
    assert user.verified_adult is False  # Default value
    assert user.is_active is True  # Default value
    assert user.created_at is not None
    assert user.updated_at is not None


def test_create_user_with_admin_role(db_session):
    """Test creating a user with admin role (AUTH-001)"""
    user = User(
        email="admin@example.com",
        name="Admin User",
        oauth_provider="microsoft",
        oauth_id="ms_456",
        role=UserRole.admin
    )
    db_session.add(user)
    db_session.commit()
    
    assert user.role == UserRole.admin


def test_create_user_with_armorer_role(db_session):
    """Test creating a user with armorer role (AUTH-001)"""
    user = User(
        email="armorer@example.com",
        name="Armorer User",
        oauth_provider="google",
        oauth_id="google_789",
        role=UserRole.armorer
    )
    db_session.add(user)
    db_session.commit()
    
    assert user.role == UserRole.armorer


def test_create_user_with_coach_role(db_session):
    """Test creating a user with coach role (AUTH-001)"""
    user = User(
        email="coach@example.com",
        name="Coach User",
        oauth_provider="google",
        oauth_id="google_101",
        role=UserRole.coach
    )
    db_session.add(user)
    db_session.commit()
    
    assert user.role == UserRole.coach


def test_create_user_with_volunteer_role(db_session):
    """Test creating a user with volunteer role (AUTH-001)"""
    user = User(
        email="volunteer@example.com",
        name="Volunteer User",
        oauth_provider="microsoft",
        oauth_id="ms_202",
        role=UserRole.volunteer
    )
    db_session.add(user)
    db_session.commit()
    
    assert user.role == UserRole.volunteer


def test_create_verified_adult(db_session):
    """Test creating a verified adult user (AUTH-002)"""
    user = User(
        email="verified@example.com",
        name="Verified Adult",
        oauth_provider="google",
        oauth_id="google_303",
        verified_adult=True
    )
    db_session.add(user)
    db_session.commit()
    
    assert user.verified_adult is True


def test_user_email_must_be_unique(db_session):
    """Test that user email must be unique"""
    user1 = User(
        email="duplicate@example.com",
        name="User One",
        oauth_provider="google",
        oauth_id="google_404"
    )
    db_session.add(user1)
    db_session.commit()
    
    # Try to create another user with the same email
    user2 = User(
        email="duplicate@example.com",
        name="User Two",
        oauth_provider="microsoft",
        oauth_id="ms_505"
    )
    db_session.add(user2)
    
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_user_email_required(db_session):
    """Test that email is required"""
    user = User(
        name="No Email User",
        oauth_provider="google",
        oauth_id="google_606"
    )
    db_session.add(user)
    
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_user_name_required(db_session):
    """Test that name is required"""
    user = User(
        email="noname@example.com",
        oauth_provider="google",
        oauth_id="google_707"
    )
    db_session.add(user)
    
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_user_oauth_provider_required(db_session):
    """Test that oauth_provider is required"""
    user = User(
        email="noprovider@example.com",
        name="No Provider User",
        oauth_id="some_id"
    )
    db_session.add(user)
    
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_user_oauth_id_required(db_session):
    """Test that oauth_id is required"""
    user = User(
        email="nooauthid@example.com",
        name="No OAuth ID User",
        oauth_provider="google"
    )
    db_session.add(user)
    
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_update_user_role(db_session):
    """Test updating user role (AUTH-001)"""
    user = User(
        email="rolechange@example.com",
        name="Role Change User",
        oauth_provider="google",
        oauth_id="google_808",
        role=UserRole.parent
    )
    db_session.add(user)
    db_session.commit()
    
    assert user.role == UserRole.parent
    
    # Update role to coach
    user.role = UserRole.coach
    db_session.commit()
    
    # Verify the change
    db_session.refresh(user)
    assert user.role == UserRole.coach


def test_update_verified_adult_flag(db_session):
    """Test updating verified adult flag (AUTH-002)"""
    user = User(
        email="verify@example.com",
        name="Verify User",
        oauth_provider="google",
        oauth_id="google_909",
        verified_adult=False
    )
    db_session.add(user)
    db_session.commit()
    
    assert user.verified_adult is False
    
    # Update verified_adult flag
    user.verified_adult = True
    db_session.commit()
    
    # Verify the change
    db_session.refresh(user)
    assert user.verified_adult is True


def test_deactivate_user(db_session):
    """Test deactivating a user account"""
    user = User(
        email="deactivate@example.com",
        name="Deactivate User",
        oauth_provider="microsoft",
        oauth_id="ms_111",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    
    assert user.is_active is True
    
    # Deactivate user
    user.is_active = False
    db_session.commit()
    
    # Verify the change
    db_session.refresh(user)
    assert user.is_active is False


def test_user_role_enum_values():
    """Test that UserRole enum has all expected values"""
    expected_roles = {'admin', 'armorer', 'coach', 'volunteer', 'parent'}
    actual_roles = {role.value for role in UserRole}
    
    assert actual_roles == expected_roles


def test_query_users_by_role(db_session):
    """Test querying users by role"""
    # Create users with different roles
    admin = User(
        email="admin1@example.com",
        name="Admin",
        oauth_provider="google",
        oauth_id="admin_1",
        role=UserRole.admin
    )
    coach = User(
        email="coach1@example.com",
        name="Coach",
        oauth_provider="google",
        oauth_id="coach_1",
        role=UserRole.coach
    )
    parent = User(
        email="parent1@example.com",
        name="Parent",
        oauth_provider="google",
        oauth_id="parent_1",
        role=UserRole.parent
    )
    
    db_session.add_all([admin, coach, parent])
    db_session.commit()
    
    # Query for coaches
    coaches = db_session.query(User).filter(User.role == UserRole.coach).all()
    assert len(coaches) == 1
    assert coaches[0].email == "coach1@example.com"


def test_query_verified_adults(db_session):
    """Test querying verified adult users (AUTH-002)"""
    # Create users with different verified_adult statuses
    verified1 = User(
        email="verified1@example.com",
        name="Verified 1",
        oauth_provider="google",
        oauth_id="ver_1",
        verified_adult=True
    )
    verified2 = User(
        email="verified2@example.com",
        name="Verified 2",
        oauth_provider="microsoft",
        oauth_id="ver_2",
        verified_adult=True
    )
    not_verified = User(
        email="notverified@example.com",
        name="Not Verified",
        oauth_provider="google",
        oauth_id="not_ver_1",
        verified_adult=False
    )
    
    db_session.add_all([verified1, verified2, not_verified])
    db_session.commit()
    
    # Query for verified adults
    verified_adults = db_session.query(User).filter(User.verified_adult == True).all()
    assert len(verified_adults) == 2
    assert all(user.verified_adult for user in verified_adults)
