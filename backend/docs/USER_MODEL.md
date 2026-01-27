# User Model Documentation

## Overview

The User model represents authenticated users in the WilcoSS Custody & Equipment Manager system. It implements role-based access control and verified adult authorization for off-site custody management.

## Related User Stories

- **AUTH-001**: As an Admin, I want to assign roles to users (Armorer, Coach, Volunteer, Parent), so that access control is properly enforced.
- **AUTH-002**: As an Admin, I want to flag users as "verified adults", so that only approved adults can accept off-site custody.

## Database Schema

### Table: `users`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | Integer | Primary Key, Auto-increment | Unique identifier for the user |
| `email` | String | Not Null, Unique, Indexed | User's email address from OAuth provider |
| `name` | String | Not Null | User's full name from OAuth provider |
| `oauth_provider` | String | Not Null | OAuth provider used for authentication ('google' or 'microsoft') |
| `oauth_id` | String | Not Null, Indexed | Unique identifier from OAuth provider |
| `role` | UserRole Enum | Not Null, Default: 'parent' | User's role in the system |
| `verified_adult` | Boolean | Default: false | Flag indicating if user is authorized for off-site custody |
| `is_active` | Boolean | Default: true | Flag indicating if user account is active |
| `created_at` | DateTime(TZ) | Server Default: now() | Timestamp when user was created |
| `updated_at` | DateTime(TZ) | Server Default: now(), On Update: now() | Timestamp when user was last updated |

### Indexes

- `ix_users_id` - Index on `id` (primary key)
- `ix_users_email` - Unique index on `email`
- `ix_users_oauth_id` - Index on `oauth_id`

## UserRole Enum

The `UserRole` enum defines the available roles in the system:

```python
class UserRole(str, enum.Enum):
    admin = "admin"
    armorer = "armorer"
    coach = "coach"
    volunteer = "volunteer"
    parent = "parent"
```

### Role Descriptions

- **admin**: System administrators with full access to all features
- **armorer**: Equipment managers responsible for kit maintenance and off-site approvals
- **coach**: Coaches who can check out kits and approve off-site custody requests
- **volunteer**: Volunteers with limited access to assist with operations
- **parent**: Parents/guardians of athletes, default role for new users

## SQLAlchemy Model

### Location
`backend/app/models/user.py`

### Usage Example

```python
from app.models.user import User, UserRole
from app.database import SessionLocal

# Create a new user
db = SessionLocal()
new_user = User(
    email="john.doe@example.com",
    name="John Doe",
    oauth_provider="google",
    oauth_id="google_123456789",
    role=UserRole.coach,
    verified_adult=True
)
db.add(new_user)
db.commit()

# Query users by role
coaches = db.query(User).filter(User.role == UserRole.coach).all()

# Query verified adults
verified_adults = db.query(User).filter(User.verified_adult == True).all()
```

## Pydantic Schemas

### Location
`backend/app/schemas/user.py`

### Available Schemas

#### UserBase
Base schema with common fields:
- `email`: EmailStr
- `name`: str

#### UserCreate
Schema for creating new users:
- Inherits from `UserBase`
- `oauth_provider`: str
- `oauth_id`: str
- `role`: UserRole (default: UserRole.parent)

#### UserResponse
Schema for API responses:
- Inherits from `UserBase`
- `id`: int
- `role`: UserRole
- `verified_adult`: bool
- `is_active`: bool
- `created_at`: datetime

#### UserUpdate
Schema for updating users:
- `role`: Optional[UserRole]
- `verified_adult`: Optional[bool]

#### Token
Schema for authentication tokens:
- `access_token`: str
- `token_type`: str (default: "bearer")
- `user`: UserResponse

## Migrations

### Initial Migration
**File**: `backend/alembic/versions/001_add_user_model.py`

Creates the `users` table with all base fields using String for the role column.

### Role Enum Migration
**File**: `backend/alembic/versions/007_convert_user_role_to_enum.py`

Converts the `role` column from String to UserRole enum type for improved type safety and validation.

#### Running Migrations

```bash
# Apply all pending migrations
cd backend
alembic upgrade head

# Rollback last migration
alembic downgrade -1

# View migration history
alembic history
```

## API Endpoints

### User Management

| Method | Endpoint | Description | Required Role |
|--------|----------|-------------|---------------|
| GET | `/api/v1/auth/me` | Get current authenticated user | Any authenticated user |
| PUT | `/api/v1/users/{user_id}` | Update user role or verified_adult flag | Admin |
| GET | `/api/v1/users` | List all users | Admin |

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/auth/google/login` | Initiate Google OAuth flow |
| GET | `/api/v1/auth/google/callback` | Google OAuth callback |
| GET | `/api/v1/auth/microsoft/login` | Initiate Microsoft OAuth flow |
| GET | `/api/v1/auth/microsoft/callback` | Microsoft OAuth callback |

## Security Considerations

1. **OAuth ID Indexing**: The `oauth_id` field is indexed to enable fast lookups during authentication.

2. **Email Uniqueness**: Email addresses must be unique across the system to prevent duplicate accounts.

3. **Verified Adult Authorization**: The `verified_adult` flag controls which users can accept off-site custody of equipment. This flag should only be set by administrators after proper vetting.

4. **Role-Based Access Control**: The `role` field is used throughout the application to enforce permission checks. Changing a user's role affects their access to features.

5. **Soft Delete**: Users are not hard-deleted. Instead, the `is_active` flag is set to `false` to preserve audit trail integrity.

## Testing

### Test Coverage

Comprehensive tests are located in `backend/tests/test_user_model.py` covering:

- User creation with default values
- All role types (admin, armorer, coach, volunteer, parent)
- Verified adult flag functionality
- Field validation and constraints
- Unique constraints (email)
- Required field validation
- Role and verified_adult updates
- User activation/deactivation
- Querying by role and verified_adult status

### Running Tests

```bash
cd backend
pytest tests/test_user_model.py -v
```

## Constants

User role constants are defined in `backend/app/constants.py`:

```python
from app.models.user import UserRole

# Valid user roles - using UserRole enum
VALID_ROLES = [role.value for role in UserRole]
DEFAULT_ROLE = UserRole.parent.value
```

These constants are used for validation in API endpoints and business logic.

## Future Enhancements

Potential improvements for the User model:

1. **Profile Picture**: Add avatar/profile picture support
2. **Contact Information**: Phone number, emergency contact
3. **Preferences**: User settings and preferences
4. **Multi-Factor Authentication**: Additional security layer
5. **Login History**: Track user login attempts and sessions
6. **Password Recovery**: Email-based account recovery (if moving away from OAuth-only)
7. **User Groups**: Group users by organization or team

## Change Log

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-26 | Initial user model with OAuth authentication |
| 1.1 | 2026-01-27 | Added UserRole enum for type safety and improved validation |
