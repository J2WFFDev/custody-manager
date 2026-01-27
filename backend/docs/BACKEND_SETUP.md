# Backend Setup Guide

This guide provides comprehensive instructions for setting up the FastAPI backend with SQLAlchemy and PostgreSQL for the WilcoSS Custody Manager.

## Architecture Overview

The backend is built with:
- **FastAPI** - Modern, high-performance Python web framework
- **SQLAlchemy 2.0** - Powerful ORM for database operations
- **PostgreSQL** - Production-grade relational database
- **Alembic** - Database migration management
- **Pydantic** - Data validation and settings management
- **Authlib** - OAuth 2.0 authentication (Google & Microsoft)

## Prerequisites

Before starting, ensure you have:
- Python 3.11 or higher
- PostgreSQL 14 or higher
- pip (Python package manager)
- Git

## Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/J2WFFDev/custody-manager.git
cd custody-manager/backend
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy the example environment file and update with your settings:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# Application
APP_NAME=WilcoSS Custody Manager API
DEBUG=True
API_V1_PREFIX=/api/v1

# Database
DATABASE_URL=postgresql://username:password@localhost:5432/custody_manager

# Security
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS - Add your frontend URLs
BACKEND_CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]

# OAuth - Google (optional for development)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# OAuth - Microsoft (optional for development)
MICROSOFT_CLIENT_ID=your-microsoft-client-id
MICROSOFT_CLIENT_SECRET=your-microsoft-client-secret

# Frontend
FRONTEND_URL=http://localhost:5173
```

### 5. Set Up PostgreSQL Database

Create a new PostgreSQL database:

```bash
# Using psql command-line tool
createdb custody_manager

# Or using SQL
psql -U postgres
CREATE DATABASE custody_manager;
\q
```

Alternatively, use a GUI tool like pgAdmin or DBeaver to create the database.

### 6. Run Database Migrations

Initialize the database schema using Alembic:

```bash
# Run all migrations to create tables
alembic upgrade head

# Check migration history
alembic history

# Check current database version
alembic current
```

### 7. Start Development Server

```bash
# Start with auto-reload for development
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or use the start script
chmod +x start.sh
./start.sh
```

The API will be available at:
- API Base: http://localhost:8000
- Swagger Docs: http://localhost:8000/api/v1/docs
- ReDoc: http://localhost:8000/api/v1/redoc
- Health Check: http://localhost:8000/health

## Project Structure

```
backend/
├── alembic/                    # Database migrations
│   ├── versions/              # Migration files
│   ├── env.py                 # Alembic environment config
│   └── script.py.mako         # Migration template
├── app/
│   ├── api/                   # API routes
│   │   └── v1/
│   │       └── endpoints/     # API endpoint modules
│   │           ├── auth.py    # Authentication endpoints
│   │           ├── kits.py    # Kit management
│   │           ├── users.py   # User management
│   │           ├── custody.py # Custody operations
│   │           ├── events.py  # Event logs
│   │           └── maintenance.py
│   ├── core/                  # Core utilities
│   │   └── security.py        # JWT and security functions
│   ├── models/                # SQLAlchemy models
│   │   ├── base.py           # Base model with common fields
│   │   ├── user.py           # User model
│   │   ├── kit.py            # Equipment kit model
│   │   ├── custody_event.py  # Custody tracking
│   │   ├── approval_request.py
│   │   └── maintenance_event.py
│   ├── schemas/               # Pydantic schemas for validation
│   │   ├── user.py
│   │   ├── kit.py
│   │   └── ...
│   ├── services/              # Business logic layer
│   │   ├── oauth.py          # OAuth authentication
│   │   ├── custody_service.py
│   │   ├── kit_service.py
│   │   ├── user_service.py
│   │   └── ...
│   ├── config.py              # Application configuration
│   ├── database.py            # Database connection setup
│   ├── constants.py           # Application constants
│   └── main.py                # FastAPI application entry point
├── docs/                      # Documentation
│   ├── OAUTH_SETUP.md        # OAuth configuration guide
│   ├── USER_MODEL.md         # User model documentation
│   └── BACKEND_SETUP.md      # This file
├── tests/                     # Test files
├── .env.example              # Example environment variables
├── .gitignore                # Git ignore rules
├── alembic.ini               # Alembic configuration
├── requirements.txt          # Python dependencies
└── README.md                 # Quick reference

```

## Database Models

### Core Models

The application uses the following main database models:

1. **User** - User accounts with role-based access control
   - Roles: Admin, Armorer, Coach, Volunteer, Parent
   - OAuth authentication support
   - Verified adult flag for off-site custody

2. **Kit** - Equipment/firearm kits
   - QR code tracking
   - Status management (available, checked_out, maintenance, lost)
   - Serial number encryption

3. **CustodyEvent** - Audit trail for custody changes
   - Append-only log
   - Event types: check_out, check_in, transfer, lost, found
   - Attestation support

4. **ApprovalRequest** - Multi-role approval workflows
   - Off-site custody approvals
   - Admin/Armorer approval tracking

5. **MaintenanceEvent** - Equipment maintenance tracking
   - Open/close maintenance sessions
   - Round counts and parts tracking

All models inherit from `BaseModel` which provides:
- Auto-incrementing `id` (primary key)
- `created_at` timestamp
- `updated_at` timestamp (auto-updates on modification)

## Database Migrations

### Creating New Migrations

When you modify models, create a new migration:

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "description of changes"

# Review the generated migration in alembic/versions/
# Edit if needed, then apply:
alembic upgrade head
```

### Common Migration Commands

```bash
# Upgrade to latest version
alembic upgrade head

# Upgrade one version
alembic upgrade +1

# Downgrade one version
alembic downgrade -1

# Show current version
alembic current

# Show migration history
alembic history --verbose

# Downgrade to specific version
alembic downgrade <revision_id>
```

### Migration Best Practices

- Always review auto-generated migrations before applying
- Test migrations on a copy of production data
- Never modify applied migrations
- Use descriptive names for migrations
- Keep migrations small and focused

## API Documentation

### Interactive Documentation

Once the server is running, access interactive API docs:

- **Swagger UI**: http://localhost:8000/api/v1/docs
  - Try out API endpoints directly
  - View request/response schemas
  - Test authentication

- **ReDoc**: http://localhost:8000/api/v1/redoc
  - Clean, three-panel documentation
  - Easy to navigate and read

### Main API Endpoints

#### Authentication
- `GET /api/v1/auth/google/login` - Initiate Google OAuth
- `GET /api/v1/auth/microsoft/login` - Initiate Microsoft OAuth
- `GET /api/v1/auth/me` - Get current user (requires token)
- `POST /api/v1/auth/refresh` - Refresh access token

#### Kits
- `GET /api/v1/kits` - List all kits
- `POST /api/v1/kits` - Create new kit
- `GET /api/v1/kits/{kit_id}` - Get kit details
- `GET /api/v1/kits/lookup/{code}` - Lookup kit by QR code
- `PUT /api/v1/kits/{kit_id}` - Update kit
- `DELETE /api/v1/kits/{kit_id}` - Delete kit

#### Custody
- `POST /api/v1/custody/checkout` - Check out kit
- `POST /api/v1/custody/checkin` - Check in kit
- `POST /api/v1/custody/transfer` - Transfer custody
- `POST /api/v1/custody/report-lost` - Report kit as lost

#### Events
- `GET /api/v1/events` - List all custody events
- `GET /api/v1/events/kit/{kit_id}` - Get events for specific kit
- `GET /api/v1/events/user/{user_id}` - Get events for specific user

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_auth_endpoints.py

# Run with verbose output
pytest -v

# Run tests matching pattern
pytest -k "test_custody"
```

### Test Database Setup

Tests use a separate test database. The `init_test_db.py` script helps set this up:

```bash
python init_test_db.py
```

## OAuth Authentication Setup

For detailed OAuth setup instructions, see [OAUTH_SETUP.md](./OAUTH_SETUP.md).

### Quick OAuth Test

1. Configure OAuth credentials in `.env`
2. Start the server
3. Navigate to: http://localhost:8000/api/v1/auth/google/login
4. Complete OAuth flow
5. You'll be redirected with a JWT token

## Development Tips

### Database Inspection

```bash
# Connect to PostgreSQL
psql custody_manager

# List tables
\dt

# Describe table
\d users

# Query data
SELECT * FROM users LIMIT 5;
```

### Debugging

Enable debug mode in `.env`:

```env
DEBUG=True
```

This enables:
- SQL query logging
- Detailed error messages
- Auto-reload on code changes

### Code Quality

```bash
# Format code with black
black app/

# Lint with flake8
flake8 app/

# Type checking with mypy
mypy app/
```

## Deployment

### Environment Variables for Production

Important settings for production:

```env
DEBUG=False
SECRET_KEY=<strong-random-key>
DATABASE_URL=<production-database-url>
BACKEND_CORS_ORIGINS=["https://yourdomain.com"]
```

### Railway Deployment

The backend is configured for Railway deployment. See [RAILWAY_DEPLOYMENT.md](./RAILWAY_DEPLOYMENT.md) for details.

Key files:
- `Procfile` - Specifies the start command
- `runtime.txt` - Python version
- `start.sh` - Startup script

## Troubleshooting

### Common Issues

**Import errors:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

**Database connection errors:**
```bash
# Check PostgreSQL is running
pg_isready

# Verify database exists
psql -l | grep custody_manager

# Check DATABASE_URL in .env
```

**Migration errors:**
```bash
# Check current migration state
alembic current

# Force migration version (use cautiously)
alembic stamp head
```

**Port already in use:**
```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
uvicorn app.main:app --reload --port 8001
```

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/20/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

## Support

For issues or questions:
- Check the [GitHub Issues](https://github.com/J2WFFDev/custody-manager/issues)
- Review the [Contributing Guide](../../CONTRIBUTING.md)
- See [User Stories](../../USER_STORIES.md) for feature context

---

**Last Updated:** January 2026  
**Author:** J2WFFDev Team
