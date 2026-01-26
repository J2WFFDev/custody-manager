# WilcoSS Custody Manager - Backend API

FastAPI backend for the WilcoSS Custody & Equipment Manager.

## Tech Stack
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - ORM for database operations
- **PostgreSQL** - Primary database
- **Alembic** - Database migrations
- **Pydantic** - Data validation
- **Authlib** - OAuth 2.0 authentication

## Prerequisites
- Python 3.11+
- PostgreSQL 14+
- pip or poetry

## Local Development Setup

1. **Create virtual environment:**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

4. **Create database:**
   ```bash
   createdb custody_manager
   ```

5. **Run migrations:**
   ```bash
   alembic upgrade head
   ```

6. **Start development server:**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

7. **Access API documentation:**
   - Swagger UI: http://localhost:8000/api/v1/docs
   - ReDoc: http://localhost:8000/api/v1/redoc

## OAuth Authentication

The application supports OAuth 2.0 authentication with Google and Microsoft providers. See [OAuth Setup Guide](docs/OAUTH_SETUP.md) for detailed configuration instructions.

### Quick OAuth Setup

1. Configure OAuth credentials in `.env`:
   ```
   GOOGLE_CLIENT_ID=your-google-client-id
   GOOGLE_CLIENT_SECRET=your-google-client-secret
   
   MICROSOFT_CLIENT_ID=your-microsoft-client-id
   MICROSOFT_CLIENT_SECRET=your-microsoft-client-secret
   ```

2. Authentication endpoints:
   - Google login: `GET /api/v1/auth/google/login`
   - Microsoft login: `GET /api/v1/auth/microsoft/login`
   - Get current user: `GET /api/v1/auth/me` (requires Bearer token)

## Project Structure
```
backend/
├── app/
│   ├── main.py          # FastAPI application
│   ├── config.py        # Configuration
│   ├── database.py      # Database connection
│   ├── models/          # SQLAlchemy models
│   ├── schemas/         # Pydantic schemas
│   ├── api/             # API endpoints
│   ├── services/        # Business logic
│   └── core/            # Core utilities
├── alembic/             # Database migrations
├── tests/               # Test files
├── docs/                # Documentation
└── requirements.txt     # Dependencies
```

## Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## Testing

```bash
pytest
```

## Deployment

See Railway deployment configuration in Issue #16.
